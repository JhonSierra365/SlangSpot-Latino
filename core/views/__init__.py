from .auth_views import (
    home,
    notifications_view, mark_notification_read,
    mark_all_notifications_read
)

from .forum_views import (
    ForumPostListView,
    ForumPostCreateView, ForumPostUpdateView,
    ForumPostDeleteView, post_detail_view,
    like_post, moderate_delete_post
)

from .lesson_views import (
    LessonListView, LessonDetailView,
    LessonCreateView, LessonUpdateView,
    LessonDeleteView, ExpressionCreateView,
    ExpressionUpdateView, ExpressionDeleteView,
    complete_lesson
)

from .chat_views import chat, get_chat_history, send_message, get_ai_response
from .profile_views import ProfileView, ProfileUpdateView
from .practice_views import (
    PracticeListView, PracticeCreateView, PracticeDetailView,
    PracticeUpdateView, PracticeDeleteView
)

from .blog_views import (
    BlogListView, BlogDetailView, BlogCreateView,
    BlogUpdateView, BlogDeleteView, blog_like
)

__all__ = [
    'chat',
    'get_chat_history',
    'send_message',
    'get_ai_response',
    'LessonListView',
    'LessonCreateView',
    'LessonDetailView',
    'LessonUpdateView',
    'LessonDeleteView',
    'ProfileView',
    'ProfileUpdateView',
    'PracticeListView',
    'PracticeCreateView',
    'PracticeDetailView',
    'PracticeUpdateView',
    'PracticeDeleteView',
    'BlogListView',
    'BlogDetailView',
    'BlogCreateView',
    'BlogUpdateView',
    'BlogDeleteView',
    'blog_like',
] 