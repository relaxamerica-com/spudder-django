from django import template
from spudderaccounts.wrappers import RoleStudent
from spudderdomain.controllers import RoleController
from spudmart.CERN.utils import strip_invalid_chars
from spudmart.CERN.models import Student
from spudmart.accounts.templatetags.accounts import user_name
from spudmart.venues.models import TempVenue

register = template.Library()


@register.simple_tag
def strip_school_name(school):
    """
    Strips invalid characters from the school name for nicer URLs
    :param school: a School object whose name we want stripped
    :return: the name of the school without any invalid characters
    """
    return strip_invalid_chars(school.name)


@register.simple_tag(takes_context=True)
def my_school_link(context, user):
    """
    Gets the link for the school of the supplied student user
    :param user: a user who is also a student
    :return: the relative link to the page for the student's school
    """
    current_role = context['request'].current_role
    if current_role.entity_type == RoleController.ENTITY_STUDENT:
        sch = current_role.entity.school
        return '/cern/%s/%s/%s' % (sch.state, sch.id, strip_invalid_chars(sch.name))
    else:
        return ''

@register.simple_tag
def student_school_link(student):
    """
    Gets the link for the school of a supplied student
    :param student: any Student object
    :return: the relative link to the page for the school if given a student
    """
    if type(student) is Student:
        sch = student.school
        return '/cern/%s/%s/%s' % (sch.state, sch.id, strip_invalid_chars(sch.name))

@register.simple_tag()
def school_rank(student):
    """
    Provides rank information as a string (X of X total students)
    :param student: a Student object
    :return: an integer between 1 and the number of students at the school
    """
    sch = student.school
    ranked_students = sorted(sch.get_students(), key=lambda s: s.rep(),
                             reverse=True)

    count = 1
    for s in ranked_students:
        if s == student:
            break
        else:
            count += 1

    return "%s of %s total students" % (count, len(ranked_students))

@register.simple_tag()
def national_rank(student):
    """
    Provides rank information as a string (X of X total students)
    :param student: a Student object
    :return: an integer between 1 and the number of total students in CERN
    """
    students = Student.objects.all()
    ranked_students = sorted(students, key=lambda s: s.rep(),
                             reverse=True)

    count = 1
    for s in ranked_students:
        if s == student:
            break
        else:
            count += 1

    return "%s of %s total students" % (count, len(ranked_students))


@register.simple_tag(takes_context=True)
def current_student_page(context):
    """

    :param context: request context
    :return: a relative url string to student page
    """
    current_role = context['request'].current_role
    if current_role.entity_type == RoleController.ENTITY_STUDENT:
        stu = current_role.entity
        return '/cern/student/%s' % (stu.id)
    else:
        return ''


@register.simple_tag()
def student_email(student):
    """
    Get the Amazon email related to a student
    :param student: any Student object
    :return: an email address as string
    """
    r = RoleStudent(student)
    email = r._amazon_id
    return email


@register.simple_tag()
def display_name(student):
    """
    Gets either the display name or the username for the student
    :param student: any Student object
    :return: a name as string
    """
    if student.display_name:
        return student.display_name
    else:
        return user_name(student.user)


@register.filter()
def student_has_temp_venues(student):
    """
    Checks to see whether the student has any temporary venues
    :param student: any Student objects
    :return: a boolean
    """
    return bool(TempVenue.objects.filter(student=student))
