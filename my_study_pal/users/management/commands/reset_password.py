from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Reset passwords for all users to a fixed password."

    def handle(self, *args, **options):
        User = get_user_model()
        fixed_password = "studypaladmin"  # 🔒 Set your fixed password here

        users = User.objects.all()
        if not users.exists():
            self.stdout.write(self.style.WARNING("⚠️ No users found."))
            return

        for user in users:
            user.set_password(fixed_password)
            user.save()

        self.stdout.write(self.style.SUCCESS(
            f"✅ Passwords for {users.count()} users have been reset to '{fixed_password}'."
        ))
