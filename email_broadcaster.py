#!/usr/bin/env python3
"""
Email Broadcaster using Google Apps Script API
Membaca daftar email dari CSV/Excel dan mengirim email secara broadcast
"""

import requests
import pandas as pd
import json
import time
from datetime import datetime
from typing import List, Dict, Optional
import os
from pathlib import Path


class EmailBroadcaster:
    """Class untuk mengirim broadcast email menggunakan Google Apps Script API"""
    
    def __init__(self, api_url: str, api_key: str):
        """
        Inisialisasi Email Broadcaster
        
        Args:
            api_url: URL endpoint Google Apps Script API
            api_key: API Key untuk autentikasi
        """
        self.api_url = api_url
        self.api_key = api_key
        self.sent_count = 0
        self.failed_count = 0
        self.results = []
    
    def load_recipients_from_csv(self, file_path: str) -> pd.DataFrame:
        """
        Load daftar penerima dari file CSV
        
        Args:
            file_path: Path ke file CSV dengan kolom 'nama' dan 'email'
            
        Returns:
            DataFrame dengan data penerima
        """
        try:
            df = pd.read_csv(file_path)
            
            # Validasi kolom yang diperlukan
            required_columns = ['nama', 'email']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Kolom yang hilang: {', '.join(missing_columns)}")
            
            # Hapus baris dengan email kosong
            df = df.dropna(subset=['email'])
            
            # Validasi format email
            df['email_valid'] = df['email'].str.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
            invalid_emails = df[~df['email_valid']]
            
            if len(invalid_emails) > 0:
                print(f"⚠️  Ditemukan {len(invalid_emails)} email tidak valid:")
                print(invalid_emails[['nama', 'email']])
                
                # Hapus email yang tidak valid
                df = df[df['email_valid']]
            
            df = df.drop('email_valid', axis=1)
            
            print(f"✅ Berhasil load {len(df)} penerima dari {file_path}")
            return df
            
        except FileNotFoundError:
            raise FileNotFoundError(f"File tidak ditemukan: {file_path}")
        except Exception as e:
            raise Exception(f"Error membaca file CSV: {str(e)}")
    
    def load_recipients_from_excel(self, file_path: str, sheet_name: str = 0) -> pd.DataFrame:
        """
        Load daftar penerima dari file Excel
        
        Args:
            file_path: Path ke file Excel
            sheet_name: Nama atau index sheet (default: 0)
            
        Returns:
            DataFrame dengan data penerima
        """
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # Validasi kolom yang diperlukan
            required_columns = ['nama', 'email']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Kolom yang hilang: {', '.join(missing_columns)}")
            
            # Hapus baris dengan email kosong
            df = df.dropna(subset=['email'])
            
            # Validasi format email
            df['email_valid'] = df['email'].str.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
            invalid_emails = df[~df['email_valid']]
            
            if len(invalid_emails) > 0:
                print(f"⚠️  Ditemukan {len(invalid_emails)} email tidak valid:")
                print(invalid_emails[['nama', 'email']])
                
                # Hapus email yang tidak valid
                df = df[df['email_valid']]
            
            df = df.drop('email_valid', axis=1)
            
            print(f"✅ Berhasil load {len(df)} penerima dari {file_path}")
            return df
            
        except FileNotFoundError:
            raise FileNotFoundError(f"File tidak ditemukan: {file_path}")
        except Exception as e:
            raise Exception(f"Error membaca file Excel: {str(e)}")
    
    def send_single_email(self, 
                         to_email: str, 
                         to_name: str,
                         subject: str, 
                         body: str,
                         html_body: Optional[str] = None,
                         from_name: str = "Broadcast System",
                         cc: Optional[str] = None,
                         bcc: Optional[str] = None) -> Dict:
        """
        Kirim email ke satu penerima
        
        Args:
            to_email: Email penerima
            to_name: Nama penerima
            subject: Subject email
            body: Isi email (plain text)
            html_body: Isi email (HTML) - opsional
            from_name: Nama pengirim
            cc: Email CC (opsional)
            bcc: Email BCC (opsional)
            
        Returns:
            Dictionary dengan hasil pengiriman
        """
        # Personalisasi email dengan nama penerima
        personalized_body = body.replace("{nama}", to_name)
        personalized_subject = subject.replace("{nama}", to_name)
        
        if html_body:
            personalized_html_body = html_body.replace("{nama}", to_name)
        else:
            personalized_html_body = None
        
        payload = {
            "endpoint": "send-email",
            "api_key": self.api_key,
            "to": to_email,
            "subject": personalized_subject,
            "body": personalized_body,
            "from_name": from_name
        }
        
        if personalized_html_body:
            payload["html_body"] = personalized_html_body
        
        if cc:
            payload["cc"] = cc
        
        if bcc:
            payload["bcc"] = bcc
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get('success'):
                self.sent_count += 1
                return {
                    'status': 'success',
                    'email': to_email,
                    'name': to_name,
                    'message': 'Email sent successfully',
                    'message_id': result.get('data', {}).get('messageId'),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                self.failed_count += 1
                return {
                    'status': 'failed',
                    'email': to_email,
                    'name': to_name,
                    'message': result.get('error', {}).get('message', 'Unknown error'),
                    'timestamp': datetime.now().isoformat()
                }
                
        except requests.exceptions.RequestException as e:
            self.failed_count += 1
            return {
                'status': 'failed',
                'email': to_email,
                'name': to_name,
                'message': f'Request error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.failed_count += 1
            return {
                'status': 'failed',
                'email': to_email,
                'name': to_name,
                'message': f'Unexpected error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def send_bulk_email(self,
                       recipients_df: pd.DataFrame,
                       subject: str,
                       body: str,
                       html_body: Optional[str] = None,
                       from_name: str = "Broadcast System",
                       delay_seconds: float = 1.0,
                       batch_size: int = 10) -> List[Dict]:
        """
        Kirim email ke banyak penerima secara batch
        
        Args:
            recipients_df: DataFrame dengan kolom 'nama' dan 'email'
            subject: Subject email (bisa pakai {nama} untuk personalisasi)
            body: Isi email (bisa pakai {nama} untuk personalisasi)
            html_body: Isi email HTML (opsional)
            from_name: Nama pengirim
            delay_seconds: Delay antar batch untuk menghindari rate limit
            batch_size: Jumlah email per batch (max 10 sesuai API limit)
            
        Returns:
            List hasil pengiriman untuk setiap email
        """
        total_recipients = len(recipients_df)
        print(f"\n📧 Memulai broadcast ke {total_recipients} penerima...")
        print(f"📦 Batch size: {batch_size} email per batch")
        print(f"⏱️  Delay: {delay_seconds} detik antar batch\n")
        
        self.results = []
        
        # Kirim email satu per satu
        for idx, row in recipients_df.iterrows():
            email = row['email']
            nama = row['nama']
            
            print(f"[{idx + 1}/{total_recipients}] Mengirim ke: {nama} ({email})", end=" ... ")
            
            result = self.send_single_email(
                to_email=email,
                to_name=nama,
                subject=subject,
                body=body,
                html_body=html_body,
                from_name=from_name
            )
            
            self.results.append(result)
            
            if result['status'] == 'success':
                print("✅ Berhasil")
            else:
                print(f"❌ Gagal: {result['message']}")
            
            # Delay untuk menghindari rate limit
            if (idx + 1) % batch_size == 0 and (idx + 1) < total_recipients:
                print(f"\n⏸️  Pause {delay_seconds} detik untuk rate limiting...\n")
                time.sleep(delay_seconds)
        
        # Tampilkan summary
        self._print_summary()
        
        return self.results
    
    def _print_summary(self):
        """Tampilkan summary hasil pengiriman"""
        print("\n" + "="*60)
        print("📊 SUMMARY PENGIRIMAN EMAIL")
        print("="*60)
        print(f"Total Email: {len(self.results)}")
        print(f"✅ Berhasil: {self.sent_count}")
        print(f"❌ Gagal: {self.failed_count}")
        print(f"📈 Success Rate: {(self.sent_count/len(self.results)*100):.2f}%")
        print("="*60 + "\n")
    
    def save_results_to_csv(self, output_file: str = "broadcast_results.csv"):
        """
        Simpan hasil broadcast ke file CSV
        
        Args:
            output_file: Nama file output
        """
        if not self.results:
            print("⚠️  Tidak ada hasil untuk disimpan")
            return
        
        df_results = pd.DataFrame(self.results)
        df_results.to_csv(output_file, index=False)
        print(f"💾 Hasil broadcast disimpan ke: {output_file}")
    
    def check_api_health(self) -> bool:
        """
        Cek status API
        
        Returns:
            True jika API berjalan normal
        """
        try:
            response = requests.get(
                f"{self.api_url}?path=health",
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ API Status: Healthy")
                print(f"   Version: {result.get('data', {}).get('version')}")
                print(f"   Services: {result.get('data', {}).get('services')}")
                return True
            else:
                print(f"❌ API Status: Error (Status Code: {response.status_code})")
                return False
                
        except Exception as e:
            print(f"❌ Error checking API health: {str(e)}")
            return False


def main():
    """Contoh penggunaan Email Broadcaster"""
    
    # Konfigurasi API
    API_URL = "<GANTI DENGAN URL API GAS>"  # Ganti dengan URL API Anda
    API_KEY = "<apikey>"
    
    # Inisialisasi broadcaster
    broadcaster = EmailBroadcaster(API_URL, API_KEY)
    
    # Cek kesehatan API
    print("🔍 Mengecek status API...")
    if not broadcaster.check_api_health():
        print("⚠️  API tidak dapat dijangkau. Pastikan URL API sudah benar.")
        return
    
    print("\n" + "="*60)
    print("EMAIL BROADCASTER - Google Apps Script API")
    print("="*60 + "\n")
    
    # Pilihan untuk load recipients
    print("Pilih sumber data penerima:")
    print("1. CSV File")
    print("2. Excel File")
    choice = input("\nPilihan Anda (1/2): ").strip()
    
    # Load recipients
    if choice == "1":
        csv_file = input("Masukkan path file CSV: ").strip()
        try:
            recipients = broadcaster.load_recipients_from_csv(csv_file)
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return
    elif choice == "2":
        excel_file = input("Masukkan path file Excel: ").strip()
        try:
            recipients = broadcaster.load_recipients_from_excel(excel_file)
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return
    else:
        print("❌ Pilihan tidak valid")
        return
    
    # Preview recipients
    print("\n📋 Preview 5 penerima pertama:")
    print(recipients.head())
    
    confirm = input("\n❓ Lanjutkan broadcast? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Broadcast dibatalkan")
        return
    
    # Konfigurasi email
    print("\n" + "="*60)
    print("KONFIGURASI EMAIL")
    print("="*60)
    
    from_name = input("Nama Pengirim: ").strip()
    subject = input("Subject Email (gunakan {nama} untuk personalisasi): ").strip()
    
    print("\nIsi Email (plain text):")
    print("(Gunakan {nama} untuk personalisasi)")
    print("(Ketik 'END' pada baris baru untuk selesai)")
    body_lines = []
    while True:
        line = input()
        if line.strip() == 'END':
            break
        body_lines.append(line)
    body = '\n'.join(body_lines)
    
    use_html = input("\nGunakan HTML body? (y/n): ").strip().lower()
    html_body = None
    if use_html == 'y':
        print("\nIsi Email (HTML):")
        print("(Gunakan {nama} untuk personalisasi)")
        print("(Ketik 'END' pada baris baru untuk selesai)")
        html_lines = []
        while True:
            line = input()
            if line.strip() == 'END':
                break
            html_lines.append(line)
        html_body = '\n'.join(html_lines)
    
    # Konfigurasi broadcast
    delay = float(input("\nDelay antar batch (detik, default 1.0): ").strip() or "1.0")
    batch_size = int(input("Batch size (default 10, max 10): ").strip() or "10")
    
    # Mulai broadcast
    print("\n🚀 Memulai broadcast email...")
    results = broadcaster.send_bulk_email(
        recipients_df=recipients,
        subject=subject,
        body=body,
        html_body=html_body,
        from_name=from_name,
        delay_seconds=delay,
        batch_size=batch_size
    )
    
    # Simpan hasil
    save_results = input("\n💾 Simpan hasil ke CSV? (y/n): ").strip().lower()
    if save_results == 'y':
        output_file = input("Nama file output (default: broadcast_results.csv): ").strip()
        if not output_file:
            output_file = "broadcast_results.csv"
        broadcaster.save_results_to_csv(output_file)
    
    print("\n✅ Broadcast selesai!")


if __name__ == "__main__":
    main()
