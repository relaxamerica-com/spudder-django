from django.core.paginator import Paginator, Page


class EntitiesPaginator(Paginator):
    def __init__(self, object_list, per_page, orphans=0, allow_empty_first_page=True):
        super(EntitiesPaginator, self).__init__(object_list, per_page, orphans, allow_empty_first_page)

    def page(self, number):
        if number > self.num_pages:
            number = self.num_pages
        if number < 1:
            number = 1
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        if top + self.orphans >= self.count:
            top = self.count
        return Page(self.object_list[bottom:top], number, self)