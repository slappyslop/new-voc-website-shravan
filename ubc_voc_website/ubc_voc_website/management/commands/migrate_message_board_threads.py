"""
SELECT message_id, forum_id, thread, user_id, subject, body, datestamp FROM `phorum_messages` WHERE parent_id=0 
"""

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.utils.timezone import make_aware

from machina.apps.forum.models import Forum
from machina.apps.forum_conversation.models import Topic, Post

import csv
from datetime import datetime

User = get_user_model()

FORUMS = {
    1: 1,
    3: 2,
    4: 3
}

class Command(BaseCommand):
    help="Migrate the first post in each thread from CSV"

    def handle(self, *args, **kwargs):
        path="message_board_threads.csv"

        forums = {old_id: Forum.objects.get(id=new_id) for old_id, new_id in FORUMS.items()}

        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, fieldnames=[
                "message_id",
                "forum_id",
                "thread",
                "user_id",
                "subject",
                "body",
                "datestamp"
            ])

            for row in reader:
                try:
                    user = User.objects.get(id=int(row["user_id"]))
                except User.DoesNotExist:
                    continue

                try:
                    message_id = row["message_id"]
                    forum_id = int(row["forum_id"])
                    timestamp = int(row["datestamp"])
                    time = make_aware(datetime.fromtimestamp(timestamp))
                except (ValueError, TypeError):
                    self.stdout.write(self.style.ERROR(f"Malformed row: {row["subject"][:30]}"))
                    continue

                topic, created = Topic.objects.get_or_create(
                    forum=forums.get(forum_id),
                    subject=row["subject"],
                    created=time,
                    defaults={
                        "poster": user,
                        "status": Topic.TOPIC_APPROVED,

                        # Since I don't have control over Machina models to add an old_id field, use the unused username field
                        "poster_username": message_id
                    }
                )

                Topic.objects.filter(pk=topic.pk).update(created=time, updated=time)
                post, post_created = Post.objects.get_or_create(
                    topic=topic,
                    created=time,
                    defaults={
                        "poster": user,
                        "poster_username": message_id,
                        "subject": row["subject"],
                        "content": row["body"]
                    }
                )

                Post.objects.filter(pk=post.pk).update(created=time, updated=time)

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created Topic and Post for: {row["subject"][:30]}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Topic already exists: {row["subject"][:30]}"))
            
            self.stdout.write(self.style.SUCCESS(f"Message board topic migration complete"))