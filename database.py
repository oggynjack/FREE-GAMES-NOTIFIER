"""
Database abstraction layer - supports JSON, MongoDB, or Hybrid
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

# MongoDB support (optional)
try:
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

class DatabaseManager:
    """Manages data storage across JSON files and/or MongoDB"""
    
    def __init__(self, mode='json', mongodb_url=None):
        """
        Initialize database manager
        
        Args:
            mode: 'json', 'mongodb', or 'hybrid'
            mongodb_url: MongoDB connection string
        """
        self.mode = mode
        self.mongodb_url = mongodb_url
        self.mongo_client = None
        self.db = None
        
        # File paths
        self.settings_file = 'settings.json'
        self.user_emails_file = 'user_emails.json'
        self.games_history_file = 'games_history.json'
        
        # Initialize MongoDB if needed
        if mode in ['mongodb', 'hybrid'] and mongodb_url and MONGODB_AVAILABLE:
            try:
                self.mongo_client = MongoClient(mongodb_url)
                self.db = self.mongo_client['epic_games_notifier']
                print(f"✅ MongoDB connected: {mode} mode")
            except Exception as e:
                print(f"❌ MongoDB connection failed: {e}")
                if mode == 'mongodb':
                    print("⚠️  Falling back to JSON mode")
                    self.mode = 'json'
    
    # Settings Management
    def read_settings(self) -> Dict:
        """Read settings from storage"""
        if self.mode in ['mongodb', 'hybrid'] and self.db:
            try:
                doc = self.db.settings.find_one({'_id': 'main'})
                if doc:
                    doc.pop('_id', None)
                    return doc
            except Exception as e:
                print(f"MongoDB read error: {e}")
        
        # JSON fallback or primary
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        return {}
    
    def write_settings(self, data: Dict):
        """Write settings to storage"""
        if self.mode in ['mongodb', 'hybrid'] and self.db:
            try:
                data_copy = data.copy()
                data_copy['_id'] = 'main'
                data_copy['updated_at'] = datetime.now().isoformat()
                self.db.settings.replace_one(
                    {'_id': 'main'},
                    data_copy,
                    upsert=True
                )
            except Exception as e:
                print(f"MongoDB write error: {e}")
        
        # JSON write (always for json/hybrid)
        if self.mode in ['json', 'hybrid']:
            with open(self.settings_file, 'w') as f:
                json.dump(data, f, indent=2)
    
    # User Emails Management
    def read_user_emails(self) -> Dict:
        """Read user email mappings"""
        if self.mode in ['mongodb', 'hybrid'] and self.db:
            try:
                result = {}
                for doc in self.db.user_emails.find():
                    fingerprint = doc.get('fingerprint')
                    email = doc.get('email')
                    if fingerprint and email:
                        result[fingerprint] = email
                if result:
                    return result
            except Exception as e:
                print(f"MongoDB read error: {e}")
        
        # JSON fallback
        if os.path.exists(self.user_emails_file):
            with open(self.user_emails_file, 'r') as f:
                return json.load(f)
        return {}
    
    def write_user_emails(self, data: Dict):
        """Write user email mappings"""
        if self.mode in ['mongodb', 'hybrid'] and self.db:
            try:
                # Clear and rewrite
                self.db.user_emails.delete_many({})
                if data:
                    docs = [
                        {'fingerprint': fp, 'email': email, 'updated_at': datetime.now().isoformat()}
                        for fp, email in data.items()
                    ]
                    self.db.user_emails.insert_many(docs)
            except Exception as e:
                print(f"MongoDB write error: {e}")
        
        # JSON write
        if self.mode in ['json', 'hybrid']:
            with open(self.user_emails_file, 'w') as f:
                json.dump(data, f, indent=2)
    
    # Games History Management
    def read_games_history(self) -> List[Dict]:
        """Read games history"""
        if self.mode in ['mongodb', 'hybrid'] and self.db:
            try:
                games = list(self.db.games_history.find().sort('found_date', -1))
                for game in games:
                    game.pop('_id', None)
                if games:
                    return games
            except Exception as e:
                print(f"MongoDB read error: {e}")
        
        # JSON fallback
        if os.path.exists(self.games_history_file):
            with open(self.games_history_file, 'r') as f:
                return json.load(f)
        return []
    
    def write_games_history(self, data: List[Dict]):
        """Write games history"""
        if self.mode in ['mongodb', 'hybrid'] and self.db:
            try:
                # Clear and rewrite
                self.db.games_history.delete_many({})
                if data:
                    for game in data:
                        game_copy = game.copy()
                        if 'found_date' not in game_copy:
                            game_copy['found_date'] = datetime.now().isoformat()
                        self.db.games_history.insert_one(game_copy)
            except Exception as e:
                print(f"MongoDB write error: {e}")
        
        # JSON write
        if self.mode in ['json', 'hybrid']:
            with open(self.games_history_file, 'w') as f:
                json.dump(data, f, indent=2)
    
    def add_game_to_history(self, game: Dict) -> List[Dict]:
        """Add a single game to history"""
        history = self.read_games_history()
        
        # Add timestamp
        if 'found_date' not in game:
            game['found_date'] = datetime.now().isoformat()
        
        # Check if exists
        existing = next((g for g in history if g.get('title') == game.get('title')), None)
        
        if not existing:
            if self.mode in ['mongodb', 'hybrid'] and self.db:
                try:
                    game_copy = game.copy()
                    self.db.games_history.insert_one(game_copy)
                except Exception as e:
                    print(f"MongoDB insert error: {e}")
            
            history.insert(0, game)
            
            if self.mode in ['json', 'hybrid']:
                with open(self.games_history_file, 'w') as f:
                    json.dump(history, f, indent=2)
        
        return history
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        stats = {
            'mode': self.mode,
            'mongodb_connected': bool(self.db),
            'mongodb_available': MONGODB_AVAILABLE,
            'settings_count': 1 if self.read_settings() else 0,
            'user_emails_count': len(self.read_user_emails()),
            'games_count': len(self.read_games_history())
        }
        
        if self.db:
            try:
                stats['mongodb_collections'] = self.db.list_collection_names()
            except:
                pass
        
        return stats
    
    def close(self):
        """Close database connections"""
        if self.mongo_client:
            self.mongo_client.close()

# Global instance
db_manager = None

def init_database(mode='json', mongodb_url=None):
    """Initialize database manager"""
    global db_manager
    db_manager = DatabaseManager(mode=mode, mongodb_url=mongodb_url)
    return db_manager

def get_db():
    """Get current database manager"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager(mode='json')
    return db_manager
