import json
import os
import time
from datetime import datetime
from pathlib import Path
from utils.logger import logger


class CandidateDatabase:
    """Database for tracking candidates and their interactions"""

    def __init__(self, db_file="db _database/candidates.json"):
        self.db_path = Path(db_file)
        self.db_dir = self.db_path.parent
        self.db_dir.mkdir(exist_ok=True)

        # Initialize database if it doesn't exist
        if not self.db_path.exists():
            self.db = {
                "candidates": {},
                "stats": {
                    "total_candidates": 0,
                    "resumes_received": 0,
                    "messages_sent": 0,
                    "last_updated": datetime.now().isoformat()
                },
                "message_history": []
            }
            self.save_db()
        else:
            self.load_db()

    def load_db(self):
        """Load database from file"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                self.db = json.load(f)
            logger.info(
                f"Loaded candidate database with {len(self.db['candidates'])} candidates")
        except Exception as e:
            logger.error(f"Error loading database: {e}")
            # Create a new database if loading fails
            self.db = {
                "candidates": {},
                "stats": {
                    "total_candidates": 0,
                    "resumes_received": 0,
                    "messages_sent": 0,
                    "last_updated": datetime.now().isoformat()
                },
                "message_history": []
            }

    def save_db(self):
        """Save database to file"""
        try:
            # Update last_updated timestamp
            self.db["stats"]["last_updated"] = datetime.now().isoformat()

            # Save with pretty formatting
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.db, f, ensure_ascii=False, indent=2)

            logger.debug("Database saved successfully")

            # Create a backup every 24 hours
            backup_file = self.db_dir / \
                f"candidates_backup_{datetime.now().strftime('%Y%m%d')}.json"
            if not backup_file.exists():
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(self.db, f, ensure_ascii=False, indent=2)
                logger.info(f"Created database backup: {backup_file}")

        except Exception as e:
            logger.error(f"Error saving database: {e}")

    def add_or_update_candidate(self, candidate_id, name, source="chat", extra_info=None):
        """
        Add or update a candidate in the database

        Args:
            candidate_id: Unique identifier for the candidate
            name: Candidate name
            source: Where the candidate was found (chat, search, etc.)
            extra_info: Any additional information about the candidate

        Returns:
            dict: The candidate record
        """
        current_time = datetime.now().isoformat()

        if candidate_id not in self.db["candidates"]:
            # Create new candidate record
            self.db["candidates"][candidate_id] = {
                "name": name,
                "status": "new",  # new, contacted, responded, resume_received, qualified, rejected
                "source": source,
                "first_seen": current_time,
                "last_updated": current_time,
                "resume_received": False,
                "resume_requested": False,
                "last_message_sent": None,
                "last_message_received": None,
                "follow_up_count": 0,
                "messages": [],
                "extra_info": extra_info or {},
                "notes": ""
            }
            self.db["stats"]["total_candidates"] += 1
            logger.info(f"Added new candidate: {name} (ID: {candidate_id})")
        else:
            # Update existing candidate
            self.db["candidates"][candidate_id]["last_updated"] = current_time

            # Only update name if it wasn't available before
            if not self.db["candidates"][candidate_id]["name"] or self.db["candidates"][candidate_id]["name"] == "Unknown":
                self.db["candidates"][candidate_id]["name"] = name

            # Update extra info if provided
            if extra_info:
                self.db["candidates"][candidate_id]["extra_info"].update(
                    extra_info)

            logger.debug(f"Updated candidate: {name} (ID: {candidate_id})")

        self.save_db()
        return self.db["candidates"][candidate_id]

    def update_candidate_status(self, candidate_id, status):
        """Update a candidate's status"""
        if candidate_id in self.db["candidates"]:
            self.db["candidates"][candidate_id]["status"] = status
            self.db["candidates"][candidate_id]["last_updated"] = datetime.now(
            ).isoformat()
            self.save_db()
            logger.info(
                f"Updated candidate {candidate_id} status to: {status}")
            return True
        else:
            logger.warning(
                f"Attempted to update non-existent candidate: {candidate_id}")
            return False

    def record_message(self, candidate_id, direction, content, has_resume=False):
        """
        Record a message sent to or received from a candidate

        Args:
            candidate_id: Candidate identifier
            direction: "outbound" or "inbound"
            content: Message content
            has_resume: Whether the message contains a resume

        Returns:
            bool: Success or failure
        """
        current_time = datetime.now().isoformat()

        # Create message record
        message = {
            "candidate_id": candidate_id,
            "direction": direction,
            "content": content,
            "timestamp": current_time,
            "has_resume": has_resume
        }

        # Add to global message history
        self.db["message_history"].append(message)

        # If candidate exists, update their record
        if candidate_id in self.db["candidates"]:
            candidate = self.db["candidates"][candidate_id]

            # Add to candidate message list
            candidate["messages"].append(message)

            # Update last message timestamp based on direction
            if direction == "outbound":
                candidate["last_message_sent"] = current_time
                candidate["resume_requested"] = True
                self.db["stats"]["messages_sent"] += 1

                if candidate["status"] == "new":
                    candidate["status"] = "contacted"

            elif direction == "inbound":
                candidate["last_message_received"] = current_time

                if candidate["status"] == "contacted":
                    candidate["status"] = "responded"

                # If message contains a resume, update status
                if has_resume:
                    candidate["resume_received"] = True
                    candidate["status"] = "resume_received"
                    self.db["stats"]["resumes_received"] += 1

            # Update last_updated timestamp
            candidate["last_updated"] = current_time

            self.save_db()
            return True
        else:
            logger.warning(
                f"Attempted to record message for non-existent candidate: {candidate_id}")
            return False

    def get_candidates_for_processing(self, max_count=10):
        """
        Get candidates that need processing, ordered by priority:
        1. New candidates who haven't been messaged
        2. Candidates who responded but no resume detected yet (need checking)
        3. Candidates who were messaged X days ago but haven't responded (need follow-up)

        Args:
            max_count: Maximum number of candidates to return

        Returns:
            list: Candidate records sorted by priority
        """
        now = datetime.now()
        candidates_to_process = []

        # First priority: New candidates who haven't been messaged
        for candidate_id, candidate in self.db["candidates"].items():
            if candidate["status"] == "new" and not candidate["resume_requested"]:
                candidates_to_process.append({
                    "id": candidate_id,
                    "record": candidate,
                    "priority": 1
                })

        # Second priority: Candidates who have responded but no resume detected
        for candidate_id, candidate in self.db["candidates"].items():
            if candidate["status"] == "responded" and not candidate["resume_received"]:
                candidates_to_process.append({
                    "id": candidate_id,
                    "record": candidate,
                    "priority": 2
                })

        # Third priority: Candidates who were messaged 2+ days ago but haven't responded
        for candidate_id, candidate in self.db["candidates"].items():
            if (candidate["status"] == "contacted" and
                candidate["last_message_sent"] and
                    candidate["follow_up_count"] < 2):

                # Check if it's been at least 2 days since last message
                last_msg = datetime.fromisoformat(
                    candidate["last_message_sent"])
                days_since = (now - last_msg).days

                if days_since >= 2:
                    candidates_to_process.append({
                        "id": candidate_id,
                        "record": candidate,
                        "priority": 3,
                        "days_since_contact": days_since
                    })

        # Sort by priority and limit to max_count
        candidates_to_process.sort(key=lambda x: x["priority"])
        return candidates_to_process[:max_count]

    def get_candidate_by_id(self, candidate_id):
        """Get candidate record by ID"""
        return self.db["candidates"].get(candidate_id)

    def get_candidates_by_status(self, status):
        """Get all candidates with a specific status"""
        return {cid: candidate for cid, candidate in self.db["candidates"].items()
                if candidate["status"] == status}

    def generate_report(self):
        """Generate a summary report of the database"""
        now = datetime.now()

        # Calculate statistics
        total_candidates = len(self.db["candidates"])
        resume_received = sum(
            1 for c in self.db["candidates"].values() if c["resume_received"])
        contacted = sum(1 for c in self.db["candidates"].values() if c["status"] in [
                        "contacted", "responded", "resume_received"])
        responded = sum(1 for c in self.db["candidates"].values(
        ) if c["status"] in ["responded", "resume_received"])
        new_candidates = sum(
            1 for c in self.db["candidates"].values() if c["status"] == "new")

        # Count candidates needing follow-up
        needs_followup = []
        for cid, candidate in self.db["candidates"].items():
            if candidate["status"] == "contacted" and candidate["last_message_sent"]:
                last_msg = datetime.fromisoformat(
                    candidate["last_message_sent"])
                days_since = (now - last_msg).days
                if days_since >= 2 and candidate["follow_up_count"] < 2:
                    needs_followup.append({
                        "id": cid,
                        "name": candidate["name"],
                        "days_since_contact": days_since
                    })

        # Generate report
        report = {
            "timestamp": now.isoformat(),
            "summary": {
                "total_candidates": total_candidates,
                "new_candidates": new_candidates,
                "contacted_candidates": contacted,
                "response_rate": round(responded / contacted * 100, 2) if contacted > 0 else 0,
                "resume_received": resume_received,
                "resume_rate": round(resume_received / contacted * 100, 2) if contacted > 0 else 0
            },
            "needing_followup": sorted(needs_followup, key=lambda x: x["days_since_contact"], reverse=True),
            # Last 10 messages
            "recent_activity": self.db["message_history"][-10:]
        }

        # Save report to file
        report_dir = Path("db _database/reports")
        report_dir.mkdir(exist_ok=True)
        report_path = report_dir / \
            f"candidate_report_{now.strftime('%Y%m%d_%H%M')}.json"

        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            logger.info(f"Generated candidate report: {report_path}")
        except Exception as e:
            logger.error(f"Error saving report: {e}")

        return report
