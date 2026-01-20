"""
SELECT parent_id, user_id, body, datestamp FROM `phorum_messages` WHERE parent_id!=0  order by datestamp asc
"""

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.utils.timezone import make_aware

from machina.apps.forum.models import Forum
from machina.apps.forum_conversation.models import Post, Topic

import csv
from datetime import datetime

User = get_user_model()

class Command(BaseCommand):
    help="Migrate thread responses (all posts after the first) from CSV"

    def handle(self, *args, **kwargs):
        path="message_board_responses.csv"

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, fieldnames=[
                "parent_id",
                "user_id",
                "body",
                "datestamp"
            ])

            for row in reader:
                try:
                    user = User.objects.get(old_id=int(row["user_id"]))
                except User.DoesNotExist:
                    continue
                
                time = make_aware(datetime.fromtimestamp(int(row["datestamp"])))
                topic = Post.objects.filter(username=row["parent_id"]).first().topic

                post, created = Post.objects.get_or_create(
                    topic=topic,
                    created=time,
                    poster=user,
                    defaults={
                        "subject": f"Re: {topic.subject}",
                        "content": row["body"]
                    }
                )

                if created:
                    topic.last_post = post

                Topic.objects.filter(pk=topic.pk).update(created=time, updated=time, last_post_on=time)
                Post.objects.filter(pk=post.pk).update(created=time, updated=time)
                Forum.objects.filter(pk=topic.forum.pk).update(last_post_on=time)

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created Post for {user.display_name} on: {row["subject"][:30]}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Post already exists for {user.display_name} on: {row["subject"][:30]}"))

            self.stdout.write(f"Synchronizing forum statistics")
            for f in Forum.objects.all():
                f.refresh_from_db()
            Forum.objects.rebuild()

            self.stdout.write(self.style.SUCCESS(f"Message board response migration complete"))
