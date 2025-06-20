import os
import threading
import tkinter as tk
from datetime import datetime
from tkinter import messagebox
from tkinter import ttk

from dotenv import load_dotenv

from api_client import WareraAPIClient
from data_manager import DataManager
from ui_manager import MilitaryUIManager

# Load environment variables
load_dotenv()


class WareraBattalionManager:
    def __init__(self, root):
        self.root = root
        self.root.title("⚔️ WARERA MILITARY COMMAND CENTER")
        self.root.geometry("1400x900")
        self.root.configure(bg="#1d2021")  # Gruvbox dark background

        # Initialize components
        self.api_client = WareraAPIClient()
        self.data_manager = DataManager()
        self.ui_manager = MilitaryUIManager(root, self)

        # Configuration
        self.current_country = tk.StringVar(value="argentina")
        self.max_players_shown = tk.IntVar(value=10)
        self.selected_battalion = tk.StringVar(value="CONDOR")

        # Available countries
        self.available_countries = self.get_available_countries()

        # Initialize UI and load data
        self.ui_manager.setup_ui()
        self.load_cached_data()

    def get_available_countries(self):
        countries = []

        try:
            countries = self.api_client.get_countries_info()
            for country in countries:
                self.data_manager.save_country(country)

        except Exception as e:
            # Avoid stopping for ex: when there is not internet
            print(e)
            pass

        if len(countries) < 1:
            countries = self.data_manager.get_countries()
            countries = [
                {
                    "country_info": {
                        "id": row[0],
                        "name": row[1],
                        "score": row[2],
                        "rank": row[3],
                        "updated_at": row[4],
                    }
                }
                for row in countries
            ]

        return [country.get("country_info").get("name") for country in countries]

    def get_bearer_token(self):
        """Get bearer token from environment or UI"""
        return self.api_client.bearer_token

    def set_bearer_token(self, token):
        """Set bearer token"""
        self.data_manager.save_token(token)
        self.api_client.set_bearer_token(token)

    def load_cached_data(self):
        """Load cached data for current country"""
        try:
            country = self.current_country.get()
            data = self.data_manager.load_country_data(country)
            token = self.data_manager.get_token()

            if token is not None:
                self.api_client.set_bearer_token(token)

            if data:
                self.ui_manager.update_displays(data)
                self.ui_manager.update_status(f"Loaded cached data for {country.upper()}")
            else:
                self.ui_manager.update_status("No cached data found")

        except Exception as e:
            self.ui_manager.update_status(f"Error loading data: {str(e)}")
            self.ui_manager.show_message("Error", f"Error loading cached data: {str(e)}", "error")

    def on_country_changed(self, event=None):
        """Handle country selection change"""
        self.load_cached_data()

    def refresh_data(self):
        """Refresh data from API"""
        if not self.api_client.bearer_token:
            self.ui_manager.show_message("Authorization Required", "Set Bearer Token in Operations Center!", "error")
            return

        self.ui_manager.show_loading("📡 Gathering intelligence...")

        # Run API call in separate thread
        thread = threading.Thread(target=self._fetch_data_thread)
        thread.daemon = True
        thread.start()

    def _fetch_data_thread(self):
        """Fetch data from API in separate thread"""
        try:
            country = self.current_country.get()

            # Use API client to fetch data
            self.ui_manager.update_status("🔍 Analyzing battlefield conditions...")
            data = self.api_client.fetch_country_data(country)

            if data:
                # Save data
                self.data_manager.save_country_data(country, data)

                # Use the merged data at the DB
                loaded_data = self.data_manager.load_country_data(country)

                # Update UI in main thread
                self.root.after(0, lambda: self._update_after_fetch(loaded_data))
            else:
                self.root.after(0, lambda: self._handle_fetch_error("No data received"))

        except Exception as e:
            print(e)

            error_message = str(e)
            self.root.after(0, lambda: self._handle_fetch_error(error_message))

    def _update_after_fetch(self, data):
        """Update UI after successful fetch"""
        self.ui_manager.hide_loading()
        self.ui_manager.update_displays(data)
        self.ui_manager.update_status("✅ INTELLIGENCE UPDATE COMPLETE")
        self.ui_manager.show_message("Mission Success", "Intelligence gathering completed successfully!", "success")

    def _handle_fetch_error(self, error_msg):
        """Handle fetch error"""
        self.ui_manager.hide_loading()
        self.ui_manager.update_status(f"⚠️ OPERATION FAILED: {error_msg}")
        self.ui_manager.show_message("Mission Failed", f"Intelligence gathering failed: {error_msg}", "error")

    def assign_players_to_battalion(self, player_names, battalion):
        """Assign players to battalion"""
        country = self.current_country.get()
        assignments = self.data_manager.get_assignments(country)

        count = 0
        for player_name in player_names:
            username_lower = player_name.lower()
            assignments[username_lower] = battalion
            count += 1

        self.data_manager.save_assignments(country, assignments)
        self.load_cached_data()
        return count

    def assign_medal(self, player_name, medal_type):
        """Assign medal to player"""
        country = self.current_country.get()
        current_week = self.get_current_week()

        success = self.data_manager.assign_medal(country, player_name, medal_type, current_week)
        if success:
            self.load_cached_data()
        return success

    def export_data(self, filename):
        """Export data to file"""
        country = self.current_country.get()
        return self.data_manager.export_data(country, filename)

    def import_data(self, filename):
        """Import data from file"""
        success = self.data_manager.import_data(filename)
        if success:
            self.load_cached_data()
        return success

    def clear_cache(self):
        """Clear cached data"""
        country = self.current_country.get()
        success = self.data_manager.clear_cache(country)
        if success:
            self.load_cached_data()
        return success

    def get_current_week(self):
        """Get current week identifier"""
        current_date = datetime.now()
        week_number = current_date.isocalendar()[1]
        year = current_date.year
        return f"week_{year}_{week_number}"


def main():
    root = tk.Tk()
    app = WareraBattalionManager(root)
    root.mainloop()


if __name__ == "__main__":
    main()
