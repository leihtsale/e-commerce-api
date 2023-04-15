from django.contrib.auth import get_user_model


def create_user(
        email='test@email.com', password='testpass', username='testusername',
        first_name='test firstname', last_name='test lastname'):
    """
    Helper function for creating a user
    """
    return get_user_model().objects.create_user(
        email=email,
        password=password,
        username=username,
        first_name=first_name,
        last_name=last_name,
    )
