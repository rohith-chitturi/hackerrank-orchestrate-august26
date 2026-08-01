import os
import pandas as pd
import numpy as np
from typing import Optional, Dict, List
import sys

# Add parent directory to path to allow importing models
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.domain import User, Group, GroupMember, Business, UserBusinessHistory, DailyFatigue

class DataLoader:
    """
    Loads contextual CSVs into memory and creates typed dictionaries (Domain Models) for rapid O(1) lookups.
    """
    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path
        
        # Load all CSVs, replace NaN with None for cleaner dataclass instantiation
        def load_csv(name):
            df = pd.read_csv(os.path.join(dataset_path, name))
            return df.replace({np.nan: None})
            
        self.users_df = load_csv("users.csv")
        self.groups_df = load_csv("groups.csv")
        self.group_members_df = load_csv("group_members.csv")
        self.business_accounts_df = load_csv("business_accounts.csv")
        self.user_business_history_df = load_csv("user_business_history.csv")
        self.daily_notification_summary_df = load_csv("daily_notification_summary.csv")
        self.images_df = load_csv("images.csv")
        self.voice_notes_df = load_csv("voice_notes.csv")
        
        # Create lookup dictionaries for O(1) access mapping to Domain Models
        self.users = {row["user_id"]: User(**row) for _, row in self.users_df.iterrows()}
        self.groups = {row["group_id"]: Group(**row) for _, row in self.groups_df.iterrows()}
        self.business_accounts = {row["business_id"]: Business(**row) for _, row in self.business_accounts_df.iterrows()}
        
        # Group members: map user_id -> dict of group_id -> GroupMember
        self.user_groups = {}
        for _, row in self.group_members_df.iterrows():
            uid = row["user_id"]
            gid = row["group_id"]
            if uid not in self.user_groups:
                self.user_groups[uid] = {}
            self.user_groups[uid][gid] = GroupMember(**row)
            
        # User business history: map user_id -> dict of business_id -> UserBusinessHistory
        self.user_business = {}
        for _, row in self.user_business_history_df.iterrows():
            uid = row["user_id"]
            bid = row["business_id"]
            if uid not in self.user_business:
                self.user_business[uid] = {}
            self.user_business[uid][bid] = UserBusinessHistory(**row)
            
        # Daily fatigue: map user_id -> date -> DailyFatigue
        self.fatigue = {}
        for _, row in self.daily_notification_summary_df.iterrows():
            uid = row["user_id"]
            date = str(row["date"])
            if uid not in self.fatigue:
                self.fatigue[uid] = {}
            self.fatigue[uid][date] = DailyFatigue(**row)
            
        # Media lookups
        self.images = self.images_df.set_index("image_id")["file_path"].to_dict()
        self.voice_notes = self.voice_notes_df.set_index("voice_note_id")["file_path"].to_dict()

    def get_user(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)
        
    def get_group(self, group_id: str) -> Optional[Group]:
        return self.groups.get(group_id)
        
    def get_business(self, business_id: str) -> Optional[Business]:
        return self.business_accounts.get(business_id)
        
    def get_user_group_relationship(self, user_id: str, group_id: str) -> Optional[GroupMember]:
        return self.user_groups.get(user_id, {}).get(group_id)
        
    def get_user_business_relationship(self, user_id: str, business_id: str) -> Optional[UserBusinessHistory]:
        return self.user_business.get(user_id, {}).get(business_id)
        
    def get_user_fatigue(self, user_id: str, date: str) -> Optional[DailyFatigue]:
        return self.fatigue.get(user_id, {}).get(date)
        
    def get_image_path(self, image_id: str) -> Optional[str]:
        return self.images.get(image_id)
        
    def get_voice_note_path(self, voice_note_id: str) -> Optional[str]:
        return self.voice_notes.get(voice_note_id)

    def load_message_history(self) -> pd.DataFrame:
        """Returns the full historical messages dataframe. Kept as DF for BM25/Embedding search."""
        return pd.read_csv(os.path.join(self.dataset_path, "message_history.csv")).replace({np.nan: None})
        
    def load_message_events(self) -> pd.DataFrame:
        """Returns the full message events dataframe."""
        return pd.read_csv(os.path.join(self.dataset_path, "message_events.csv")).replace({np.nan: None})
