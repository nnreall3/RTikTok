import sys
import subprocess
import os

def auto_setup():

    is_venv = sys.prefix != sys.base_prefix or 'VIRTUAL_ENV' in os.environ
    
    if not is_venv:
        venv_dir = os.path.join(os.path.dirname(__file__), "venv")
        if not os.path.exists(venv_dir):
            print("[*] First time setup: Creating an isolated virtual environment (venv)...")
            try:
                subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
            except Exception as e:
                print(f"[!] Error creating venv: {e}")
                sys.exit(1)
        

        if os.name == "nt":
            venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
        else:
            venv_python = os.path.join(venv_dir, "bin", "python")
            
        print("[*] Switching to virtual environment...")

        os.execv(venv_python, [venv_python] + sys.argv)

    required_packages = {
        "customtkinter": "customtkinter",
        "playwright": "playwright",
        "playwright_stealth": "playwright-stealth"
    }
    
    missing_packages = []
    for module_name, pip_name in required_packages.items():
        try:
            __import__(module_name)
        except ImportError:
            missing_packages.append(pip_name)
            
    if missing_packages:
        print(f"[*] Found missing packages inside venv: {missing_packages}. Installing safely...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing_packages])
            print("[*] Python packages installed successfully inside venv.")
        except Exception as e:
            print(f"[!] Error installing python packages: {e}")
            sys.exit(1)

    flag_file = os.path.join(os.path.dirname(__file__), ".playwright_ready")
    if not os.path.exists(flag_file):
        print("[*] Setting up Chromium browser components inside venv...")
        try:
            subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
            with open(flag_file, "w") as f:
                f.write("ready")
            print("[*] Browser environment is fully configured.")
        except Exception as e:
            print(f"[!] Error installing Chromium components: {e}")
            sys.exit(1)

auto_setup()

import customtkinter as ctk 
import asyncio
import threading
from playwright.async_api import async_playwright

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SocialScanner(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("RTikTok")
        self.geometry("850x700")

        self.label = ctk.CTkLabel(self, text="TikTok Auditor & Band Assest", font=("Roboto", 24, "bold"))
        self.label.pack(pady=20)

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username (e.g. user_123)", width=350)
        self.username_entry.pack(pady=10)

        self.scan_button = ctk.CTkButton(self, text="Audit Profile", command=self.run_thread, font=("Roboto", 14, "bold"))
        self.scan_button.pack(pady=20)

        self.status_label = ctk.CTkLabel(self, text="Status: Idle", text_color="gray")
        self.status_label.pack()

        self.output_box = ctk.CTkTextbox(self, width=760, height=400, font=("Consolas", 13))
        self.output_box.pack(pady=20)

        self.report_database = {
            "Fraud/Scam (النصب والاحتيال)": {
                "keywords": [
                    "crypto", "whatsapp", "money", "free", "ربح", "استثمار", "تداول", "شحن", "فلوس", 
                    "منصة", "ثغرة", "ربح سريع", "كاش", "طريقة الربح", "1000$", "فودافون كاش", "تعبئة", "مسابقة"
                ],
                "severity": "CRITICAL (Auto-Ban Trigger)",
                "path": "Report Account -> Frauds and Scams -> Financial Scams / Impersonation",
                "note": "TikTok AI closely tracks external links and financial magic words. Mass-report triggers instant freeze."
            },
            "Hate Speech / Harassment (الكراهية والتحرش)": {
                "keywords": [
                    "hate", "attack", "ugly", "عنصري", "قتل", "حمار", "كلب", "كافر", "ملحد", "شفار", 
                    "الحمار", "الكلب", "القرود", "بوليساريو", "خائن", "تفوه", "اللعنة", "ديوث"
                ],
                "severity": "HIGH",
                "path": "Report Account -> Harassment or Bullying -> Targeted Harassment",
                "note": "Flags bullying targeted at individuals. The system cross-checks user captions and names."
            },
            "Inappropriate/Adult Content (محتوى غير لائق)": {
                "keywords": [
                    "18+", "link in bio", "adult", "سكس", "متحول", "بث مباشر +18", "قحبة", "شرموطة", 
                    "نودز", "nudes", "روتيني", "روتيني اليومي", "مؤخرة", "بث ساخن", "sex", "hot", "xxx", "ass", "pussy", "bot telegrame", "dih" "dick"
                ],
                "severity": "IMMEDIATE BAN",
                "path": "Report Account -> Nudity and Sexual Content -> Sexual Exploitation",
                "note": "Zero tolerance grid. The AI immediately nukes the account if keywords match video captions or bio."
            }
        }

    def log(self, message):
        self.output_box.insert("end", message + "\n")
        self.output_box.see("end")

    def run_thread(self):
        username = self.username_entry.get().strip()
        if not username:
            self.log("[!] Error: Please enter a username.")
            return
        
        self.scan_button.configure(state="disabled")
        self.status_label.configure(text="Status: Scanning...", text_color="green")
        self.output_box.delete("0.0", "end")
        
        threading.Thread(target=self.start_async_logic, args=(username,), daemon=True).start()

    def start_async_logic(self, username):
        asyncio.run(self.analyze_tiktok(username))

    async def analyze_tiktok(self, username):
        self.log(f"[*] Launching Scanner for target: @{username}")
        
        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(headless=False)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 720},
                    locale="ar-MA"
                )
                page = await context.new_page()

                await page.goto(f"https://www.tiktok.com/@{username}", wait_until="domcontentloaded", timeout=60000)
                await asyncio.sleep(7)
                
                # userScan
                username_text = ""
                display_name_text = ""
                
                try:
                    u_el = page.locator('h1[data-e2e="user-title"]')
                    if await u_el.count() > 0:
                        username_text = await u_el.inner_text()
                        
                    n_el = page.locator('h2[data-e2e="user-subtitle"]')
                    if await n_el.count() > 0:
                        display_name_text = await n_el.inner_text()
                except:
                    pass
                # --------------------------------------------------

                # bioScan
                bio_text = ""
                try:
                    bio_element = page.locator('[data-e2e="user-bio"]')
                    if await bio_element.count() > 0:
                        bio_text = await bio_element.inner_text()
                except: pass

                # pfpScan
                photo_desc = ""
                try:
                    photo_element = page.locator('img[class*="Avatar"]')
                    if await photo_element.count() > 0:
                        photo_desc = await photo_element.first.get_attribute("alt") or ""
                except: pass

                # vidCaptionsScan
                video_captions = []
                try:
                    videos = page.locator('[data-e2e="user-post-item-desc"]')
                    count = await videos.count()
                    self.log(f"[*] Found {count} visible videos on the first grid.")
                    for i in range(count):
                        cap_text = await videos.nth(i).inner_text()
                        if cap_text:
                            video_captions.append(cap_text)
                except: pass
                
                all_videos_text = " ".join(video_captions)

                
                self.log("-" * 40)
                self.log(f"[i] Target Meta Inspected:")
                self.log(f"    -> Target User: {username_text if username_text else username}")
                self.log(f"    -> Target Name: {display_name_text if display_name_text else '[Not Found]'}")
                self.log(f"    -> Bio Text: {bio_text if bio_text else '[Empty]'}")
                self.log(f"    -> Photo Metadata: {photo_desc if photo_desc else '[No Metadata]'}")
                self.log(f"    -> Captured Video Captions: {len(video_captions)} titles.")
                self.log("-" * 40)

               
                full_target_data = f"{username_text} {display_name_text} {bio_text} {photo_desc} {all_videos_text}".lower()

                detected_violations = []

                for violation_name, data in self.report_database.items():
                    for word in data["keywords"]:
                        if word.lower() in full_target_data:
                            detected_violations.append(violation_name)
                            break

                self.log("\n" + "="*65)
                self.log("                 AUDITING REPORT SUMMARY                 ")
                self.log("="*65)

                if detected_violations:
                    self.log(f"[!] WARNING: Target profile contains illegal content.")
                    for violation in set(detected_violations):
                        info = self.report_database[violation]
                        self.log(f"\n[+] DETECTED: {violation}")
                        self.log(f"    - Threat Level: {info['severity']}")
                        self.log(f"    - FASTEST BAN PATH (مسار الإبلاغ الأسرع):")
                        self.log(f"      👉 {info['path']}")
                        self.log(f"    - Strategy Note: {info['note']}")
                else:
                    self.log("[✔] CLEAN: No standard violations found across Username, Bio, Photo, or Video Captions.")
                
                self.log("="*65)

            except Exception as e:
                self.log(f"[!] Error: {str(e)}")
            
            finally:
                await browser.close()
                self.scan_button.configure(state="normal")
                self.status_label.configure(text="Status: Done", text_color="green")

if __name__ == "__main__":
    app = SocialScanner()
    app.mainloop()