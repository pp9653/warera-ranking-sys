import sqlite3
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime


class DataManager:
    def __init__(self, db_path: str = "data/warera.db"):
        self.db_path = db_path
        self.ensure_data_directory()
        self.init_database()

    def ensure_data_directory(self):
        """Ensure data directory exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def init_database(self):
        """Initialize SQLite database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                -- Countries table
                CREATE TABLE IF NOT EXISTS countries (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    weekly_damage INTEGER DEFAULT 0,
                    active_population INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Players table
                CREATE TABLE IF NOT EXISTS players (
                    id TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    level INTEGER DEFAULT 1,
                    avatar_url TEXT,
                    country_id TEXT,
                    weekly_damage INTEGER DEFAULT 0,
                    global_rank INTEGER DEFAULT 0,
                    country_rank INTEGER DEFAULT 0,
                    battalion TEXT DEFAULT 'UNASSIGNED',
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (country_id) REFERENCES countries (id)
                );
                
                -- Medals table
                CREATE TABLE IF NOT EXISTS medals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id TEXT,
                    player_username TEXT,
                    medal_type TEXT CHECK(medal_type IN ('gold', 'silver', 'bronze')),
                    week_identifier TEXT,
                    country_id TEXT,
                    awarded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (player_id) REFERENCES players (id),
                    UNIQUE(player_id, week_identifier)
                );
                
                -- Create indexes for better performance
                CREATE INDEX IF NOT EXISTS idx_players_country ON players(country_id);
                CREATE INDEX IF NOT EXISTS idx_players_battalion ON players(battalion);
                CREATE INDEX IF NOT EXISTS idx_medals_week ON medals(week_identifier);
                CREATE INDEX IF NOT EXISTS idx_medals_player ON medals(player_id);
            """)

    def save_country_data(self, country_name: str, data: Dict) -> bool:
        """Save country data to SQLite database"""
        try:
            country_id = country_name.lower()
            users = data.get('users', [])
            country_info = data.get('country_info', {})

            with sqlite3.connect(self.db_path) as conn:
                # Save country info
                conn.execute(
                    """
                    INSERT OR REPLACE INTO countries 
                    (id, name, weekly_damage, active_population, last_updated)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                    (
                        country_id,
                        country_info.get('name', country_name.capitalize()),
                        data.get('country_weekly_damage', 0),
                        data.get('active_population', len(users)),
                    ),
                )

                # Save players
                for i, user in enumerate(users, 1):
                    conn.execute(
                        """
                        INSERT INTO players (
                            id, username, level, avatar_url, country_id, weekly_damage,
                            global_rank, country_rank, last_updated
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                        ON CONFLICT(id) DO UPDATE SET
                            username=excluded.username,
                            level=excluded.level,
                            avatar_url=excluded.avatar_url,
                            country_id=excluded.country_id,
                            weekly_damage=excluded.weekly_damage,
                            global_rank=excluded.global_rank,
                            country_rank=excluded.country_rank,
                            last_updated=CURRENT_TIMESTAMP
                        """,
                        (
                            user.get('_id', f"{country_id}_{user['name']}"),
                            user['name'],
                            user.get('level', 1),
                            user.get('avatarUrl', ''),
                            country_id,
                            user.get('weeklyDamage', 0),
                            user.get('weeklyRankingPosition', 0),
                            i,
                        ),
                    )

            return True

        except Exception as e:
            print(f"Error saving country data: {e}")
            return False

    def load_country_data(self, country_name: str) -> Optional[Dict]:
        """Load country data from SQLite database"""
        try:
            country_id = country_name.lower()

            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                # Get country info
                country_cursor = conn.execute("SELECT * FROM countries WHERE id = ?", (country_id,))
                country_row = country_cursor.fetchone()

                if not country_row:
                    return None

                # Get players
                players_cursor = conn.execute(
                    """
                    SELECT * FROM players 
                    WHERE country_id = ? 
                    ORDER BY weekly_damage DESC
                """,
                    (country_id,),
                )
                players = players_cursor.fetchall()

                # Get assignments (battalion info from players table)
                assignments = {}
                for player in players:
                    if player['battalion'] != 'UNASSIGNED':
                        assignments[player['username'].lower()] = player['battalion']

                # Get medals data
                medals_cursor = conn.execute(
                    """
                    SELECT player_username, medal_type, week_identifier 
                    FROM medals 
                    WHERE country_id = ?
                """,
                    (country_id,),
                )
                medals_data = medals_cursor.fetchall()

                # Organize medals by user
                user_data = {}
                for medal in medals_data:
                    username_lower = medal['player_username'].lower()
                    if username_lower not in user_data:
                        user_data[username_lower] = {"medals": {}}
                    user_data[username_lower]["medals"][medal['week_identifier']] = medal['medal_type']

                # Convert players to list format
                users_list = []
                for player in players:
                    users_list.append(
                        {
                            '_id': player['id'],
                            'name': player['username'],
                            'level': player['level'],
                            'avatarUrl': player['avatar_url'] or '',
                            'weeklyDamage': player['weekly_damage'],
                            'weeklyRankingPosition': player['global_rank'],
                            'countryRankingPosition': player['country_rank'],
                        }
                    )

                return {
                    'users': users_list,
                    'country_weekly_damage': country_row['weekly_damage'],
                    'active_population': country_row['active_population'],
                    'country_info': {'_id': country_row['id'], 'name': country_row['name']},
                    'assignments': assignments,
                    'user_data': user_data,
                    'current_week': self._get_current_week(),
                    'last_updated': country_row['last_updated'],
                }

        except Exception as e:
            print(f"Error loading country data: {e}")
            return None

    def get_assignments(self, country_name: str) -> Dict:
        """Get player assignments for country"""
        try:
            country_id = country_name.lower()
            assignments = {}

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT username, battalion 
                    FROM players 
                    WHERE country_id = ? AND battalion != 'UNASSIGNED'
                """,
                    (country_id,),
                )

                for row in cursor.fetchall():
                    assignments[row[0].lower()] = row[1]

            return assignments

        except Exception as e:
            print(f"Error getting assignments: {e}")
            return {}

    def save_assignments(self, country_name: str, assignments: Dict) -> bool:
        """Save player assignments"""
        try:
            country_id = country_name.lower()

            with sqlite3.connect(self.db_path) as conn:
                for username_lower, battalion in assignments.items():
                    conn.execute(
                        """
                        UPDATE players 
                        SET battalion = ?, last_updated = CURRENT_TIMESTAMP
                        WHERE country_id = ? AND LOWER(username) = ?
                    """,
                        (battalion, country_id, username_lower),
                    )

            return True

        except Exception as e:
            print(f"Error saving assignments: {e}")
            return False

    def assign_medal(self, country_name: str, player_name: str, medal_type: str, week: str) -> bool:
        """Assign medal to player"""
        try:
            country_id = country_name.lower()

            with sqlite3.connect(self.db_path) as conn:
                # Get player ID
                cursor = conn.execute(
                    """
                    SELECT id FROM players 
                    WHERE country_id = ? AND LOWER(username) = ?
                """,
                    (country_id, player_name.lower()),
                )

                player_row = cursor.fetchone()
                if not player_row:
                    return False

                player_id = player_row[0]

                # Insert or update medal
                conn.execute(
                    """
                    INSERT OR REPLACE INTO medals 
                    (player_id, player_username, medal_type, week_identifier, country_id)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (player_id, player_name, medal_type, week, country_id),
                )

            return True

        except Exception as e:
            print(f"Error assigning medal: {e}")
            return False

    def get_player_medals(self, country_name: str, player_name: str) -> Dict:
        """Get medals for a player"""
        try:
            country_id = country_name.lower()

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT medal_type, week_identifier 
                    FROM medals 
                    WHERE country_id = ? AND LOWER(player_username) = ?
                """,
                    (country_id, player_name.lower()),
                )

                medals = {}
                for row in cursor.fetchall():
                    medals[row[1]] = row[0]  # week -> medal_type

                return medals

        except Exception as e:
            print(f"Error getting player medals: {e}")
            return {}

    def get_battalion_stats(self, country_name: str) -> List[Dict]:
        """Get battalion statistics"""
        try:
            country_id = country_name.lower()

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT 
                        battalion,
                        COUNT(*) as soldier_count,
                        SUM(weekly_damage) as total_damage,
                        AVG(weekly_damage) as avg_damage
                    FROM players 
                    WHERE country_id = ?
                    GROUP BY battalion
                    ORDER BY total_damage DESC
                """,
                    (country_id,),
                )

                stats = []
                for row in cursor.fetchall():
                    stats.append(
                        {
                            'battalion_name': row[0] or 'UNASSIGNED',
                            'soldier_count': row[1],
                            'total_damage': row[2] or 0,
                            'avg_damage': row[3] or 0,
                        }
                    )

                return stats

        except Exception as e:
            print(f"Error getting battalion stats: {e}")
            return []

    def export_data(self, country_name: str, filename: str) -> bool:
        """Export country data to JSON file"""
        try:
            data = self.load_country_data(country_name)
            if data:
                export_data = {"country": country_name, "export_timestamp": datetime.now().isoformat(), **data}

                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                return True
            return False

        except Exception as e:
            print(f"Error exporting data: {e}")
            return False

    def import_data(self, filename: str) -> bool:
        """Import data from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            country = data.get("country")
            if country:
                # Save the imported data
                success = self.save_country_data(country, data)

                # Save assignments if present
                if "assignments" in data and success:
                    self.save_assignments(country, data["assignments"])

                return success
            return False

        except Exception as e:
            print(f"Error importing data: {e}")
            return False

    def clear_cache(self, country_name: str) -> bool:
        """Clear cached data for country"""
        try:
            country_id = country_name.lower()

            with sqlite3.connect(self.db_path) as conn:
                # Delete in correct order due to foreign keys
                conn.execute("DELETE FROM medals WHERE country_id = ?", (country_id,))
                conn.execute("DELETE FROM players WHERE country_id = ?", (country_id,))
                conn.execute("DELETE FROM countries WHERE id = ?", (country_id,))

            return True

        except Exception as e:
            print(f"Error clearing cache: {e}")
            return False

    def get_database_info(self) -> Dict:
        """Get database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT 
                        (SELECT COUNT(*) FROM countries) as countries_count,
                        (SELECT COUNT(*) FROM players) as players_count,
                        (SELECT COUNT(*) FROM medals) as medals_count
                """)

                row = cursor.fetchone()
                return {'countries': row[0], 'players': row[1], 'medals': row[2], 'database_path': self.db_path}

        except Exception as e:
            print(f"Error getting database info: {e}")
            return {}

    def _get_current_week(self) -> str:
        """Get current week identifier"""
        current_date = datetime.now()
        week_number = current_date.isocalendar()[1]
        year = current_date.year
        return f"week_{year}_{week_number}"

    def vacuum_database(self):
        """Optimize database by running VACUUM"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("VACUUM")
            return True
        except Exception as e:
            print(f"Error vacuuming database: {e}")
            return False

    def save_token(self, token_value: str) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO tokens (name, token, last_updated)
                    VALUES ('default', ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(name) DO UPDATE SET token=excluded.token, last_updated=CURRENT_TIMESTAMP
                    """,
                    (token_value,),
                )
            return True
        except Exception as e:
            print(f"Error saving token: {e}")
            return False

    def get_token(self) -> Optional[str]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT token FROM tokens WHERE name = 'default'")
                row = cursor.fetchone()
                if row:
                    return row[0]
                else:
                    return None
        except Exception as e:
            print(f"Error retrieving token: {e}")
            return None

    def save_country(self, country):
        country_info = country.get('country_info', {})
        country_id = country_info.get("name", "Unknown").lower()
        country_name = country_id
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO countries
                    (id, name, weekly_damage, active_population, last_updated)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                    (
                        country_id,
                        country_info.get('name', country_name.capitalize()),
                        country_info.get('rankings', {}).get('weeklyCountryDamages', {}).get("value", 0),
                        country_info.get('rankings', {}).get('countryActivePopulation', {}).get("value", 0),
                    ),
                )
            return True
        except Exception as e:
            print(f"Error saving token: {e}")
            return False

    def get_countries(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                countries_cursor = conn.execute(
                    """
                    SELECT * FROM countries
                    """
                )
                countries = countries_cursor.fetchall()
                return countries
        except Exception as e:
            print(e)
