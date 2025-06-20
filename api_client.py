import json
import os
import random
import time
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import requests
from rich.console import Console

console = Console()

BEARER_TOKEN = os.getenv("WARERA_BEARER_TOKEN")
BATCH_SIZE = 10
MAX_TOTAL_SOLDIERS = 150


class WareraAPIClient:
    BASE_URL = "https://api2.warera.io/trpc"

    def __init__(self):
        self.bearer_token = BEARER_TOKEN
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"{self.bearer_token}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Referer": "https://app.warera.io/",
                "Origin": "https://app.warera.io",
            }
        )

    def set_bearer_token(self, token: str):
        """Set the bearer token for API authentication"""
        self.bearer_token = token
        self.session.headers.update({'Authorization': f'{token}', 'Content-Type': 'application/json'})

    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Internal GET request with delay and error handling"""
        delay = random.uniform(2, 8)
        time.sleep(delay)
        try:
            url = f"{self.BASE_URL}/{endpoint}"
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            console.print(f"[red]API request failed: {e}[/red]")
            return None

    def get_country_info(self, country_name: str) -> Dict:
        """Gets country data including weekly damage totals and active population"""
        url = "https://api2.warera.io/countries"
        response = self.session.get(url)
        response.raise_for_status()

        countries = response.json()
        for country in countries:
            if country.get("name", "").lower() == country_name.lower():
                console.print(f"[green]Found country: {country_name.capitalize()}[/green]")

                rankings = country.get("rankings", {})
                weekly_damage_data = rankings.get("weeklyCountryDamages", {})
                weekly_damage = weekly_damage_data.get("value", 0)
                weekly_rank = weekly_damage_data.get("rank", 0)

                active_population_data = rankings.get("countryActivePopulation", {})
                active_population = active_population_data.get("value", 0)
                population_rank = active_population_data.get("rank", 0)

                return {
                    "country_info": country,
                    "country_id": country.get('_id'),
                    "weekly_damage": weekly_damage,
                    "weekly_rank": weekly_rank,
                    "active_population": active_population,
                    "population_rank": population_rank,
                }

        raise ValueError(f"Country '{country_name}' not found.")

    def get_countries_info(self) -> Dict:
        """Gets country data including weekly damage totals and active population"""
        url = "https://api2.warera.io/countries"
        response = self.session.get(url)
        response.raise_for_status()

        all_countries = []

        countries = response.json()
        for country in countries:
            rankings = country.get("rankings", {})
            weekly_damage_data = rankings.get("weeklyCountryDamages", {})
            weekly_damage = weekly_damage_data.get("value", 0)
            weekly_rank = weekly_damage_data.get("rank", 0)

            active_population_data = rankings.get("countryActivePopulation", {})
            active_population = active_population_data.get("value", 0)
            population_rank = active_population_data.get("rank", 0)

            all_countries.append(
                {
                    "country_info": country,
                    "country_id": country.get('_id'),
                    "weekly_damage": weekly_damage,
                    "weekly_rank": weekly_rank,
                    "active_population": active_population,
                    "population_rank": population_rank,
                }
            )

        return all_countries

    def get_global_ranking(self) -> List[Dict]:
        """Gets complete global ranking"""
        endpoint = "ranking.getRanking"
        all_ranking_data = []
        cursor = None

        console.print("[cyan]Fetching global ranking...[/cyan]")

        while True:
            input_data = {"0": {"rankingType": "weeklyUserDamages"}}
            if cursor:
                input_data["0"]["cursor"] = cursor

            params = {"batch": "1", "input": json.dumps(input_data)}

            data = self._make_request(endpoint, params=params)
            if not data or not isinstance(data, list) or not data[0].get("result"):
                break

            result = data[0]["result"]
            page_data = result.get("data", {})
            items = page_data.get("items", [])
            if not items:
                break

            all_ranking_data.extend(items)
            console.print(f"[dim]Got {len(all_ranking_data)} users so far...[/dim]")

            cursor = page_data.get("nextCursor")
            if not cursor:
                break

        console.print(f"[green]Complete ranking: {len(all_ranking_data)} users[/green]")

        return sorted(all_ranking_data, key=lambda x: x.get("value", 0), reverse=True)

    def get_users_by_country(self, country_id: str) -> List[Dict]:
        # Ta roto
        """Gets ALL users by country"""
        endpoint = "user.getUsersByCountry"
        all_users = []
        cursor = None

        console.print("[cyan]Fetching country users...[/cyan]")

        while True:
            input_data = {"0": {"countryId": country_id, "direction": "forward"}}

            if cursor:
                input_data["0"]["cursor"] = cursor

            params = {"batch": "1", "input": json.dumps(input_data)}

            data = self._make_request(endpoint, params=params)
            if not data or not isinstance(data, list):
                break

            result = data[0].get("result", {})
            items = result.get("data", {}).get("items", [])
            if not items:
                break

            all_users.extend(items)
            cursor = result.get("data", {}).get("nextCursor")
            if not cursor:
                break

        console.print(f"[green]Found {len(all_users)} users from country[/green]")
        return all_users

    def get_users_details_batch(self, user_ids: List[str], batch_size: int = 25) -> List[Dict]:
        """Gets user details in batches"""
        if not user_ids:
            return []

        user_ids_batch = user_ids[:batch_size]
        input_data = {str(i): {"userId": user_id} for i, user_id in enumerate(user_ids_batch)}

        endpoint_parts = ["user.getUserLite"] * len(user_ids_batch)
        endpoint = ",".join(endpoint_parts)

        params = {"batch": "1", "input": json.dumps(input_data)}

        data = self._make_request(endpoint, params=params)
        users_details = []

        if isinstance(data, list):
            for item in data:
                if "result" in item and "data" in item["result"]:
                    users_details.append(item["result"]["data"])

        return users_details

    def fetch_country_data(self, country_name: str) -> Optional[Dict]:
        """Fetch complete country data including users and rankings"""
        console.print(f"[green]Fetching data for {country_name}[/green]")

        # Step 1: Get country information using the new method
        country_data = self.get_country_info(country_name)
        if not country_data:
            raise Exception(f"Could not find country: {country_name}")

        country_info = country_data["country_info"]
        country_id = country_data["country_id"]

        if not country_id:
            raise Exception(f"Invalid country data for: {country_name}")

        console.print(f"[green]Found country: {country_info.get('name')} (ID: {country_id})[/green]")

        # Step 2: Get global ranking to find country users
        console.print("[green]Fetching global ranking[/green]")
        global_ranking = self.get_global_ranking()  # Get more users to ensure we catch all country users

        if not global_ranking:
            raise Exception("Could not fetch global ranking")

        # Step 3: Filter users by country
        country_users = self.filter_users_by_country(global_ranking, country_id, country_name)

        if not country_users:
            console.print(f"[red]No users found for country {country_name}[/red]")
            country_users = []

        for user in global_ranking:
            if user.get('country', {}).get('_id') == country_id:
                country_users.append(user)

        console.print(f"[green]Found {len(country_users)} users from {country_name}[/green]")

        # Step 4: Add ranking positions within country
        country_users.sort(key=lambda x: x.get('weeklyDamage', 0), reverse=True)
        for i, user in enumerate(country_users, 1):
            user['countryRankingPosition'] = i

        # Step 5: Prepare final data structure using the new country data
        result = {
            'country_info': country_info,
            'users': country_users,
            'country_weekly_damage': country_data["weekly_damage"],
            'active_population': country_data["active_population"],
            'current_week': self._get_current_week(),
            'last_updated': datetime.now().isoformat(),
        }

        console.print(
            f"[green]Data collection complete: {country_data['active_population']} users, {country_data['weekly_damage']:,} total damage[/green]"
        )
        return result

    def _get_current_week(self) -> str:
        """Get current week identifier"""
        current_date = datetime.now()
        week_number = current_date.isocalendar()[1]
        year = current_date.year
        return f"week_{year}_{week_number}"

    def filter_users_by_country(self, ranking_data, country_id, country_name):
        """Filters users from ranking data by country ID"""
        console.print(f"[cyan]Filtering users by country...[/cyan]")

        country_user_items = self.get_users_by_country(country_id)

        if not country_user_items:
            return []

        country_user_ids = set(item.get('_id') for item in country_user_items if item.get('_id'))

        country_ranking_entries = []
        for rank_entry in ranking_data:
            user_id = rank_entry.get('user')
            if user_id in country_user_ids:
                country_ranking_entries.append(rank_entry)

        console.print(f"[green]Found {len(country_ranking_entries)} ranked users from country[/green]")

        if not country_ranking_entries:
            return []

        ranking_user_ids = [entry.get('user') for entry in country_ranking_entries]

        all_user_details = []
        for i in range(0, len(ranking_user_ids), BATCH_SIZE):
            batch_ids = ranking_user_ids[i : i + BATCH_SIZE]
            batch_details = self.get_users_details_batch(batch_ids)
            all_user_details.extend(batch_details)

        user_details_map = {user.get('_id'): user for user in all_user_details if user.get('_id')}

        filtered_users = []

        for rank_entry in country_ranking_entries:
            user_id = rank_entry.get('user')
            if user_id in user_details_map:
                user_details = user_details_map[user_id]
                name = user_details.get("username", "Unknown")

                user = {
                    "_id": user_id,
                    "name": name,
                    "username": name,
                    "weeklyDamage": rank_entry.get("value", 0),
                    "weeklyRankingPosition": rank_entry.get("rank", 0),
                    "countryId": country_id,
                    "level": user_details.get("leveling", {}).get("level", 1),
                    "avatarUrl": user_details.get("avatarUrl", ""),
                }
                filtered_users.append(user)

        filtered_users.sort(key=lambda x: x['weeklyDamage'], reverse=True)

        if len(filtered_users) > MAX_TOTAL_SOLDIERS:
            console.print(f"[yellow]Limiting to top {MAX_TOTAL_SOLDIERS} users[/yellow]")
            filtered_users = filtered_users[:MAX_TOTAL_SOLDIERS]

        return filtered_users

    def get_users_details_batch(self, user_ids: List[str]):
        """Gets user details in batches"""
        if not user_ids:
            return []

        batch_size = min(BATCH_SIZE, len(user_ids))
        user_ids_batch = user_ids[:batch_size]

        input_data = {}
        for i, user_id in enumerate(user_ids_batch):
            input_data[str(i)] = {"userId": user_id}

        endpoint_parts = ["user.getUserLite"] * len(user_ids_batch)
        endpoint = f"{','.join(endpoint_parts)}"

        params = {"batch": "1", "input": json.dumps(input_data)}

        data = self._make_request(f"{endpoint}?batch={params['batch']}&input={params['input']}")

        users_details = []

        if isinstance(data, list):
            for item in data:
                if "result" in item and "data" in item["result"]:
                    users_details.append(item["result"]["data"])

        return users_details
