"""Test data generator for creating datasets with various bad data scenarios."""

import random
import string
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import uuid


class DataGenerator:
    """
    Generates test data with configurable error scenarios.
    
    Useful for testing ETL pipelines and validators.
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize data generator.
        
        Args:
            seed: Random seed for reproducibility
        """
        if seed is not None:
            random.seed(seed)
        
        self.first_names = ['John', 'Jane', 'Bob', 'Alice', 'Charlie', 'Diana', 'Eve', 'Frank']
        self.last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller']
        self.cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia']
        self.companies = ['TechCorp', 'DataInc', 'CloudSys', 'DevWorks', 'CodeLab', 'ByteFactory']
    
    def generate_user_record(
        self,
        include_errors: bool = False,
        error_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a user record.
        
        Args:
            include_errors: Whether to include errors
            error_types: Types of errors to include:
                - 'missing_field': Missing required fields
                - 'invalid_format': Invalid data formats
                - 'invalid_type': Wrong data types
                - 'out_of_range': Values out of valid range
                - 'invalid_email': Invalid email format
                - 'invalid_date': Invalid date format
        
        Returns:
            User record dictionary
        """
        # Generate valid record
        record = {
            'id': str(uuid.uuid4()),
            'first_name': random.choice(self.first_names),
            'last_name': random.choice(self.last_names),
            'email': f'{self._random_string(8)}@example.com',
            'age': random.randint(18, 80),
            'city': random.choice(self.cities),
            'registration_date': self._random_date().strftime('%Y-%m-%d'),
            'is_active': random.choice([True, False]),
            'score': round(random.uniform(0, 100), 2),
        }
        
        # Add errors if requested
        if include_errors and error_types:
            for error_type in error_types:
                if random.random() < 0.3:  # 30% chance for each error
                    self._inject_error(record, error_type)
        
        return record
    
    def generate_transaction_record(
        self,
        include_errors: bool = False,
        error_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate a transaction record."""
        record = {
            'transaction_id': str(uuid.uuid4()),
            'user_id': str(uuid.uuid4()),
            'amount': round(random.uniform(10, 1000), 2),
            'currency': random.choice(['USD', 'EUR', 'GBP', 'JPY']),
            'timestamp': datetime.now().isoformat(),
            'status': random.choice(['pending', 'completed', 'failed']),
            'merchant': random.choice(self.companies),
        }
        
        if include_errors and error_types:
            for error_type in error_types:
                if random.random() < 0.3:
                    self._inject_error(record, error_type)
        
        return record
    
    def generate_product_record(
        self,
        include_errors: bool = False,
        error_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate a product record."""
        record = {
            'product_id': str(uuid.uuid4()),
            'name': f'Product {self._random_string(5)}',
            'category': random.choice(['Electronics', 'Clothing', 'Food', 'Books', 'Toys']),
            'price': round(random.uniform(5, 500), 2),
            'stock': random.randint(0, 1000),
            'description': f'This is a sample product description {self._random_string(20)}',
            'created_at': self._random_date().strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        if include_errors and error_types:
            for error_type in error_types:
                if random.random() < 0.3:
                    self._inject_error(record, error_type)
        
        return record
    
    def generate_dataset(
        self,
        record_type: str = 'user',
        count: int = 100,
        error_rate: float = 0.2,
        error_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate a dataset with configurable error rate.
        
        Args:
            record_type: Type of record ('user', 'transaction', 'product')
            count: Number of records to generate
            error_rate: Percentage of records with errors (0.0 to 1.0)
            error_types: List of error types to include
        
        Returns:
            List of records
        """
        generator_map = {
            'user': self.generate_user_record,
            'transaction': self.generate_transaction_record,
            'product': self.generate_product_record,
        }
        
        if record_type not in generator_map:
            raise ValueError(f"Unknown record type: {record_type}")
        
        generator = generator_map[record_type]
        error_types = error_types or [
            'missing_field', 'invalid_format', 'invalid_type', 
            'out_of_range', 'invalid_email', 'invalid_date'
        ]
        
        records = []
        for _ in range(count):
            include_errors = random.random() < error_rate
            record = generator(include_errors=include_errors, error_types=error_types)
            records.append(record)
        
        return records
    
    def _inject_error(self, record: Dict[str, Any], error_type: str):
        """Inject an error into a record."""
        if error_type == 'missing_field':
            # Remove a random field
            if record:
                field = random.choice(list(record.keys()))
                del record[field]
        
        elif error_type == 'invalid_format':
            # Corrupt a format (e.g., email, date)
            if 'email' in record:
                record['email'] = 'invalid-email'
            elif 'registration_date' in record:
                record['registration_date'] = '2024-13-45'  # Invalid date
        
        elif error_type == 'invalid_type':
            # Wrong data type
            if 'age' in record:
                record['age'] = 'twenty'  # Should be integer
            elif 'is_active' in record:
                record['is_active'] = 'yes'  # Should be boolean
            elif 'price' in record:
                record['price'] = 'expensive'  # Should be number
        
        elif error_type == 'out_of_range':
            # Value out of valid range
            if 'age' in record:
                record['age'] = random.choice([-5, 150, 999])
            elif 'score' in record:
                record['score'] = random.choice([-10, 150, 1000])
            elif 'stock' in record:
                record['stock'] = -100
        
        elif error_type == 'invalid_email':
            if 'email' in record:
                record['email'] = random.choice([
                    'notanemail',
                    '@example.com',
                    'user@',
                    'user name@example.com',
                ])
        
        elif error_type == 'invalid_date':
            if 'registration_date' in record:
                record['registration_date'] = random.choice([
                    '2024-13-01',  # Invalid month
                    '2024-02-30',  # Invalid day
                    '99/99/9999',  # Wrong format
                    'not-a-date',
                ])
            elif 'created_at' in record:
                record['created_at'] = 'invalid-timestamp'
            elif 'timestamp' in record:
                record['timestamp'] = '2024-99-99T99:99:99'
    
    def _random_string(self, length: int) -> str:
        """Generate a random string."""
        return ''.join(random.choices(string.ascii_lowercase, k=length))
    
    def _random_date(self, days_back: int = 365) -> datetime:
        """Generate a random date within the last N days."""
        days = random.randint(0, days_back)
        return datetime.now() - timedelta(days=days)
    
    @staticmethod
    def save_to_csv(records: List[Dict[str, Any]], file_path: str):
        """Save records to CSV file."""
        import csv
        
        if not records:
            return
        
        fieldnames = list(records[0].keys())
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)
    
    @staticmethod
    def save_to_json(records: List[Dict[str, Any]], file_path: str):
        """Save records to JSON file."""
        import json
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def save_to_jsonl(records: List[Dict[str, Any]], file_path: str):
        """Save records to JSON Lines file."""
        import json
        
        with open(file_path, 'w', encoding='utf-8') as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')

