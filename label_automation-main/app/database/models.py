import sqlite3
import json
import os
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class EasyPostAccount:
    """EasyPost account configuration"""
    id: str
    name: str
    api_key: str
    webhook_secret: Optional[str] = None
    is_active: bool = True
    created_at: str = None
    updated_at: str = None

@dataclass 
class PrinterConfig:
    """Printer configuration for an account"""
    id: str
    account_id: str
    printer_name: str
    printnode_api_key: str
    printer_id: str
    is_default: bool = False
    is_active: bool = True
    created_at: str = None
    updated_at: str = None

class AccountDatabase:
    """Database manager for accounts and printers"""
    
    def __init__(self, db_path: str = "accounts.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # EasyPost accounts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS easypost_accounts (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    api_key TEXT NOT NULL,
                    webhook_secret TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Printer configurations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS printer_configs (
                    id TEXT PRIMARY KEY,
                    account_id TEXT NOT NULL,
                    printer_name TEXT NOT NULL,
                    printnode_api_key TEXT NOT NULL,
                    printer_id TEXT NOT NULL,
                    is_default BOOLEAN DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (account_id) REFERENCES easypost_accounts (id)
                )
            ''')
            
            conn.commit()
    
    def add_easypost_account(self, account: EasyPostAccount) -> bool:
        """Add a new EasyPost account"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO easypost_accounts (id, name, api_key, webhook_secret, is_active)
                    VALUES (?, ?, ?, ?, ?)
                ''', (account.id, account.name, account.api_key, account.webhook_secret, account.is_active))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding EasyPost account: {e}")
            return False
    
    def get_easypost_account(self, account_id: str) -> Optional[EasyPostAccount]:
        """Get EasyPost account by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM easypost_accounts WHERE id = ?', (account_id,))
                row = cursor.fetchone()
                
                if row:
                    return EasyPostAccount(
                        id=row[0], name=row[1], api_key=row[2], webhook_secret=row[3],
                        is_active=bool(row[4]), created_at=row[5], updated_at=row[6]
                    )
                return None
        except Exception as e:
            print(f"Error getting EasyPost account: {e}")
            return None
    
    def get_all_easypost_accounts(self) -> List[EasyPostAccount]:
        """Get all EasyPost accounts"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM easypost_accounts WHERE is_active = 1')
                rows = cursor.fetchall()
                
                accounts = []
                for row in rows:
                    accounts.append(EasyPostAccount(
                        id=row[0], name=row[1], api_key=row[2], webhook_secret=row[3],
                        is_active=bool(row[4]), created_at=row[5], updated_at=row[6]
                    ))
                return accounts
        except Exception as e:
            print(f"Error getting EasyPost accounts: {e}")
            return []
    
    def add_printer_config(self, printer: PrinterConfig) -> bool:
        """Add a new printer configuration"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO printer_configs (id, account_id, printer_name, printnode_api_key, printer_id, is_default, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (printer.id, printer.account_id, printer.printer_name, 
                      printer.printnode_api_key, printer.printer_id, printer.is_default, printer.is_active))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding printer config: {e}")
            return False
    
    def get_printers_for_account(self, account_id: str) -> List[PrinterConfig]:
        """Get all printer configurations for an account"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM printer_configs WHERE account_id = ? AND is_active = 1', (account_id,))
                rows = cursor.fetchall()
                
                printers = []
                for row in rows:
                    printers.append(PrinterConfig(
                        id=row[0], account_id=row[1], printer_name=row[2],
                        printnode_api_key=row[3], printer_id=row[4], is_default=bool(row[5]),
                        is_active=bool(row[6]), created_at=row[7], updated_at=row[8]
                    ))
                return printers
        except Exception as e:
            print(f"Error getting printer configs: {e}")
            return []
    
    def get_default_printer_for_account(self, account_id: str) -> Optional[PrinterConfig]:
        """Get the default printer for an account"""
        printers = self.get_printers_for_account(account_id)
        for printer in printers:
            if printer.is_default:
                return printer
        # If no default, return the first active printer
        return printers[0] if printers else None
    
    def update_easypost_account(self, account: EasyPostAccount) -> bool:
        """Update an EasyPost account"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE easypost_accounts 
                    SET name = ?, api_key = ?, webhook_secret = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (account.name, account.api_key, account.webhook_secret, account.is_active, account.id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating EasyPost account: {e}")
            return False
    
    def delete_easypost_account(self, account_id: str) -> bool:
        """Soft delete an EasyPost account"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE easypost_accounts SET is_active = 0 WHERE id = ?', (account_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting EasyPost account: {e}")
            return False
    
    def export_config(self) -> Dict:
        """Export all configurations as JSON"""
        accounts = self.get_all_easypost_accounts()
        config = {
            "accounts": [],
            "export_timestamp": datetime.now().isoformat()
        }
        
        for account in accounts:
            account_data = asdict(account)
            account_data["printers"] = [asdict(p) for p in self.get_printers_for_account(account.id)]
            config["accounts"].append(account_data)
        
        return config
    
    def import_config(self, config: Dict) -> bool:
        """Import configurations from JSON"""
        try:
            for account_data in config.get("accounts", []):
                # Create account
                printers = account_data.pop("printers", [])
                account = EasyPostAccount(**account_data)
                self.add_easypost_account(account)
                
                # Create printers
                for printer_data in printers:
                    printer = PrinterConfig(**printer_data)
                    self.add_printer_config(printer)
            
            return True
        except Exception as e:
            print(f"Error importing config: {e}")
            return False 