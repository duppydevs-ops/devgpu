from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'current_page': self.page.number,
            'previous_page': self.page.previous_page_number() if self.page.has_previous() else None,
            'next_page': self.page.next_page_number() if self.page.has_next() else None,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'count': {
                    'type': 'integer',
                    'example': 9,
                },
                'current_page': {
                    'type': 'string',
                    'nullable': True,
                    'example': 2
                },
                'previous_page': {
                    'type': 'integer',
                    'nullable': True,
                    'example': 1,
                },
                'next_page': {
                    'type': 'integer',
                    'nullable': True,
                    'example': 3,
                },
                'total_pages': {
                    'type': 'integer',
                    'example': 3,
                },
                'results': schema,
            },
        }
