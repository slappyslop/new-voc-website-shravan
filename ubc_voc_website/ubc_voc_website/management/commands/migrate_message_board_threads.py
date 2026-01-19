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

        with open(path, newline="", encoding="utf-8") as f:
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

                time = make_aware(datetime.fromtimestamp(int(row["datestamp"])))
                forum = forums.get(int(row["forum_id"]))

                topic, created = Topic.objects.get_or_create(
                    forum=forum,
                    subject=row["subject"],
                    created=time,
                    defaults={
                        "poster": user,
                        "status": Topic.TOPIC_APPROVED,
                    }
                )

                if not created:
                    self.stdout.write(self.style.WARNING(f"Topic already exists: {row["subject"]}"))
                else:
                    self.stdout.write(self.style.SUCCESS(f"Migrated topic: {row["subject"]}"))

                Topic.objects.filter(pk=topic.pk).update(created=time, updated=time)
            
            self.stdout.write(self.style.SUCCESS(f"Message board topic migration complete"))