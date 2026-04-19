"""
Bill Tracker Module
Manages and tracks all bills with storage and retrieval functionality
"""

import os
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

class BillTracker:
    """Main class for tracking bills"""
    
    def __init__(self, data_dir: str = "data", log_dir: str = "logs"):
        """
        Initialize the Bill Tracker
        
        Args:
            data_dir: Directory to store bill data
            log_dir: Directory for logs
        """
        self.data_dir = Path(data_dir)
        self.log_dir = Path(log_dir)
        self.bills_file = self.data_dir / "bills.json"
        self.csv_file = self.data_dir / "bills.csv"
        
        # Create directories if they don't exist
        self.data_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)
        
        # Initialize data file
        self.bills = self.load_bills()
    
    def load_bills(self) -> List[Dict]:
        """Load bills from JSON file"""
        if self.bills_file.exists():
            try:
                with open(self.bills_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.log(f"Error loading bills: {e}")
                return []
        return []
    
    def save_bills(self) -> bool:
        """Save bills to JSON file"""
        try:
            with open(self.bills_file, 'w') as f:
                json.dump(self.bills, f, indent=2)
            self.log(f"Bills saved successfully. Total bills: {len(self.bills)}")
            return True
        except Exception as e:
            self.log(f"Error saving bills: {e}")
            return False
    
    def add_bill(self, name: str, amount: float, due_date: str, 
                 category: str = "Other", frequency: str = "monthly") -> bool:
        """
        Add a new bill
        
        Args:
            name: Bill name (e.g., "Electricity", "Netflix")
            amount: Bill amount
            due_date: Due date (DD-MM-YYYY format)
            category: Bill category (Utilities, Subscription, Insurance, etc.)
            frequency: Frequency (daily, weekly, monthly, yearly)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            bill = {
                "id": len(self.bills) + 1,
                "name": name,
                "amount": amount,
                "due_date": due_date,
                "category": category,
                "frequency": frequency,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "paid": False,
                "payment_history": []
            }
            
            self.bills.append(bill)
            self.save_bills()
            self.log(f"Bill added: {name} - ${amount}")
            print(f"✅ Bill added successfully: {name}")
            return True
            
        except Exception as e:
            self.log(f"Error adding bill: {e}")
            print(f"❌ Error adding bill: {e}")
            return False
    
    def view_bills(self) -> None:
        """Display all bills in a formatted table"""
        if not self.bills:
            print("📭 No bills found. Add some bills first!")
            return
        
        print("\n" + "="*100)
        print(f"{'ID':<5} {'Name':<20} {'Amount':<12} {'Due Date':<12} {'Category':<15} {'Frequency':<12} {'Paid':<6}")
        print("="*100)
        
        for bill in self.bills:
            paid_status = "✅ Yes" if bill.get("paid") else "❌ No"
            print(f"{bill['id']:<5} {bill['name']:<20} ${bill['amount']:<11.2f} {bill['due_date']:<12} {bill['category']:<15} {bill['frequency']:<12} {paid_status:<6}")
        
        print("="*100 + "\n")
    
    def mark_paid(self, bill_id: int, payment_amount: Optional[float] = None) -> bool:
        """
        Mark a bill as paid
        
        Args:
            bill_id: ID of the bill to mark as paid
            payment_amount: Amount paid (defaults to bill amount)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            for bill in self.bills:
                if bill['id'] == bill_id:
                    bill['paid'] = True
                    payment = {
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "amount": payment_amount or bill['amount']
                    }
                    bill['payment_history'].append(payment)
                    self.save_bills()
                    self.log(f"Bill marked as paid: {bill['name']}")
                    print(f"✅ Bill '{bill['name']}' marked as paid!")
                    return True
            
            print(f"❌ Bill with ID {bill_id} not found!")
            return False
            
        except Exception as e:
            self.log(f"Error marking bill as paid: {e}")
            print(f"❌ Error: {e}")
            return False
    
    def get_bill_by_id(self, bill_id: int) -> Optional[Dict]:
        """Get a specific bill by ID"""
        for bill in self.bills:
            if bill['id'] == bill_id:
                return bill
        return None
    
    def get_bills_by_category(self, category: str) -> List[Dict]:
        """Get all bills in a specific category"""
        return [bill for bill in self.bills if bill['category'].lower() == category.lower()]
    
    def get_total_monthly_bills(self) -> float:
        """Calculate total monthly bill amount"""
        monthly_bills = [bill for bill in self.bills if bill['frequency'].lower() == 'monthly']
        return sum(bill['amount'] for bill in monthly_bills)
    
    def export_to_csv(self) -> bool:
        """Export bills to CSV file"""
        try:
            if not self.bills:
                print("❌ No bills to export!")
                return False
            
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['id', 'name', 'amount', 'due_date', 'category', 'frequency', 'paid'])
                writer.writeheader()
                
                for bill in self.bills:
                    writer.writerow({
                        'id': bill['id'],
                        'name': bill['name'],
                        'amount': bill['amount'],
                        'due_date': bill['due_date'],
                        'category': bill['category'],
                        'frequency': bill['frequency'],
                        'paid': bill['paid']
                    })
            
            self.log(f"Bills exported to CSV: {self.csv_file}")
            print(f"✅ Bills exported to {self.csv_file}")
            return True
            
        except Exception as e:
            self.log(f"Error exporting to CSV: {e}")
            print(f"❌ Error exporting: {e}")
            return False
    
    def delete_bill(self, bill_id: int) -> bool:
        """Delete a bill by ID"""
        try:
            for i, bill in enumerate(self.bills):
                if bill['id'] == bill_id:
                    bill_name = bill['name']
                    self.bills.pop(i)
                    self.save_bills()
                    self.log(f"Bill deleted: {bill_name}")
                    print(f"✅ Bill '{bill_name}' deleted!")
                    return True
            
            print(f"❌ Bill with ID {bill_id} not found!")
            return False
            
        except Exception as e:
            self.log(f"Error deleting bill: {e}")
            print(f"❌ Error: {e}")
            return False
    
    def log(self, message: str) -> None:
        """Log messages to file"""
        log_file = self.log_dir / "bill_tracker.log"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            with open(log_file, 'a') as f:
                f.write(f"[{timestamp}] {message}\n")
        except Exception as e:
            print(f"Error writing to log: {e}")
    
    def get_statistics(self) -> Dict:
        """Get bill statistics"""
        total_amount = sum(bill['amount'] for bill in self.bills)
        paid_bills = len([bill for bill in self.bills if bill['paid']])
        unpaid_bills = len([bill for bill in self.bills if not bill['paid']])
        
        return {
            "total_bills": len(self.bills),
            "total_amount": total_amount,
            "paid_bills": paid_bills,
            "unpaid_bills": unpaid_bills,
            "monthly_total": self.get_total_monthly_bills()
        }


def main():
    """Main function with interactive menu"""
    tracker = BillTracker()
    
    print("\n" + "="*50)
    print("💰 BILL REMINDER AI SYSTEM 💰")
    print("="*50 + "\n")
    
    while True:
        print("\n📋 Main Menu:")
        print("1. ➕ Add a new bill")
        print("2. 👀 View all bills")
        print("3. ✅ Mark bill as paid")
        print("4. 🗑️  Delete a bill")
        print("5. 📊 View statistics")
        print("6. 📁 Export to CSV")
        print("7. 🔍 View bills by category")
        print("8. 📈 View bill details")
        print("9. ❌ Exit")
        
        choice = input("\n👉 Enter your choice (1-9): ").strip()
        
        if choice == '1':
            print("\n➕ Add New Bill")
            name = input("Bill name (e.g., Electricity): ").strip()
            try:
                amount = float(input("Amount ($): "))
                due_date = input("Due date (DD-MM-YYYY): ").strip()
                category = input("Category (Utilities/Subscription/Insurance/Other): ").strip()
                frequency = input("Frequency (daily/weekly/monthly/yearly): ").strip()
                
                tracker.add_bill(name, amount, due_date, category, frequency)
            except ValueError:
                print("❌ Invalid input! Please enter correct values.")
        
        elif choice == '2':
            tracker.view_bills()
        
        elif choice == '3':
            tracker.view_bills()
            try:
                bill_id = int(input("Enter bill ID to mark as paid: "))
                tracker.mark_paid(bill_id)
            except ValueError:
                print("❌ Invalid ID!")
        
        elif choice == '4':
            tracker.view_bills()
            try:
                bill_id = int(input("Enter bill ID to delete: "))
                tracker.delete_bill(bill_id)
            except ValueError:
                print("❌ Invalid ID!")
        
        elif choice == '5':
            stats = tracker.get_statistics()
            print("\n📊 Bill Statistics:")
            print(f"   Total Bills: {stats['total_bills']}")
            print(f"   Total Amount: ${stats['total_amount']:.2f}")
            print(f"   Paid Bills: {stats['paid_bills']}")
            print(f"   Unpaid Bills: {stats['unpaid_bills']}")
            print(f"   Monthly Total: ${stats['monthly_total']:.2f}")
        
        elif choice == '6':
            tracker.export_to_csv()
        
        elif choice == '7':
            category = input("Enter category to search: ").strip()
            bills = tracker.get_bills_by_category(category)
            if bills:
                print(f"\n📂 Bills in '{category}' category:")
                for bill in bills:
                    print(f"   - {bill['name']}: ${bill['amount']}")
            else:
                print(f"❌ No bills found in '{category}' category!")
        
        elif choice == '8':
            try:
                bill_id = int(input("Enter bill ID: "))
                bill = tracker.get_bill_by_id(bill_id)
                if bill:
                    print(f"\n📄 Bill Details:")
                    for key, value in bill.items():
                        print(f"   {key}: {value}")
                else:
                    print(f"❌ Bill with ID {bill_id} not found!")
            except ValueError:
                print("❌ Invalid ID!")
        
        elif choice == '9':
            print("\n👋 Thank you for using Bill Reminder AI! Goodbye!")
            break
        
        else:
            print("❌ Invalid choice! Please enter 1-9.")


if __name__ == "__main__":
    main()