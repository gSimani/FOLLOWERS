from celery import shared_task
from django.utils import timezone
from .models import FollowTask, Schedule, Analytics
from .scrapers.factory import ScraperFactory
import twitter
from django.conf import settings

@shared_task
def process_follow_task(task_id):
    task = FollowTask.objects.get(id=task_id)
    task.status = 'running'
    task.save()

    try:
        if task.platform.name.lower() == 'twitter':
            api = twitter.Api(
                consumer_key=settings.TWITTER_CONSUMER_KEY,
                consumer_secret=settings.TWITTER_CONSUMER_SECRET,
                access_token_key=task.social_profile.access_token,
                access_token_secret=task.social_profile.access_token_secret
            )

            if task.action == 'follow':
                api.CreateFriendship(screen_name=task.target_username)
            else:  # unfollow
                api.DestroyFriendship(screen_name=task.target_username)
        else:
            # Use appropriate scraper for the platform
            scraper = ScraperFactory.get_scraper(
                task.platform.name,
                username=task.social_profile.username,
                password=task.social_profile.access_token
            )

            if task.action == 'follow':
                success = scraper.follow_user(task.target_username)
            else:  # unfollow
                success = scraper.unfollow_user(task.target_username)

            if not success:
                raise Exception("Failed to perform action")

        task.status = 'completed'
        task.save()

    except Exception as e:
        task.status = 'failed'
        task.error_message = str(e)
        task.save()
    finally:
        ScraperFactory.close_all()

@shared_task
def process_schedules():
    current_time = timezone.now().time()
    active_schedules = Schedule.objects.filter(
        is_active=True,
        start_time__lte=current_time,
        end_time__gte=current_time
    )

    for schedule in active_schedules:
        # Create follow/unfollow tasks based on schedule
        FollowTask.objects.create(
            user=schedule.user,
            platform=schedule.platform,
            social_profile=schedule.social_profile,
            action=schedule.action,
            target_username='placeholder'  # You would need logic to determine target users
        )

@shared_task
def update_analytics():
    today = timezone.now().date()
    
    # Process each social profile
    for profile in SocialProfile.objects.select_related('platform', 'user').all():
        try:
            if profile.platform.name.lower() == 'twitter':
                api = twitter.Api(
                    consumer_key=settings.TWITTER_CONSUMER_KEY,
                    consumer_secret=settings.TWITTER_CONSUMER_SECRET,
                    access_token_key=profile.access_token,
                    access_token_secret=profile.access_token_secret
                )

                user = api.GetUser(screen_name=profile.username)
                followers_count = user.followers_count
                following_count = user.friends_count
                engagement_rate = calculate_engagement_rate(user)
            else:
                # Use appropriate scraper for the platform
                scraper = ScraperFactory.get_scraper(
                    profile.platform.name,
                    username=profile.username,
                    password=profile.access_token
                )

                profile_info = scraper.get_profile_info(profile.username)
                if profile_info:
                    followers_count = int(profile_info['followers'].replace(',', ''))
                    following_count = int(profile_info['following'].replace(',', ''))
                    engagement_rate = calculate_engagement_rate_from_info(profile_info)
                else:
                    raise Exception("Failed to get profile info")

            Analytics.objects.update_or_create(
                user=profile.user,
                platform=profile.platform,
                social_profile=profile,
                date=today,
                defaults={
                    'followers_count': followers_count,
                    'following_count': following_count,
                    'engagement_rate': engagement_rate
                }
            )

        except Exception as e:
            print(f"Error updating analytics for {profile.username}: {str(e)}")
        finally:
            ScraperFactory.close_all()

def calculate_engagement_rate(user):
    """Calculate engagement rate for Twitter user"""
    if user.followers_count > 0:
        return (user.favourites_count + user.statuses_count) / user.followers_count * 100
    return 0.0

def calculate_engagement_rate_from_info(profile_info):
    """Calculate engagement rate from scraped profile info"""
    followers = int(profile_info['followers'].replace(',', ''))
    if followers > 0:
        # This is a simplified calculation - you might want to use more metrics
        return 5.0  # Return a default engagement rate
    return 0.0 