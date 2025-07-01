from django import template

from ..models import Rental

register = template.Library()

@register.filter(name='table_row_class')
def table_row_class(status):
    return {
        Rental.RentalStatus.OUT_ON_TIME: "table-success",
        Rental.RentalStatus.RETURNED_LATE: "table-warning",
        Rental.RentalStatus.OUT_LATE: "table-danger",
        Rental.RentalStatus.LOST: "table-info"
    }.get(status, "")