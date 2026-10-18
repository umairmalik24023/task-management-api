from rest_framework.pagination import PageNumberPagination


class TaskPagination(PageNumberPagination):
    # Return five tasks per page by default.
    page_size = 5

    # Allow clients to choose a different page size using ?page_size=10.
    page_size_query_param = "page_size"

    # Prevent clients from requesting excessively large pages.
    max_page_size = 20
    
    """
    What do these settings mean?
    
    =>  PageNumberPagination: DRF's built-in pagination system.

    => page_size = 5: The default number of tasks returned per page.

    => page_size_query_param: Enables clients to request a custom page size.

    => max_page_size = 20: Limits the client to 20 tasks per page, even if they request more.
    """
    
    