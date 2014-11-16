import logging
import traceback
import datetime
from django.shortcuts import render_to_response
from django.contrib import messages

from google.appengine.ext import blobstore

from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from spudderadmin.decorators import admin_login_required
from spudderadmin.leagueathletics.forms import LeagueAthleticsFormAction, LeagueAthleticsImportClubsForm, \
    LeagueAthleticsResetClubsForm, LeagueAthleticsImportedClubsSearchForm
from spudderadmin.leagueathletics.models import LeagueAthleticsImport
from spudderadmin.leagueathletics.utils import fetch_programs_for_zip, save_club_from_program_json_data
from spudderdomain.models import Club
from spudmart.upload.forms import UploadForm
from spudmart.utils.Paginator import EntitiesPaginator
from spudmart.utils.queues import trigger_backend_task


@admin_login_required
def dashboard(request):
    imported_clubs_count = Club.objects.filter(original_domain_name='leagueathletics').count()
    if not imported_clubs_count:
        imported_clubs_count = 0

    upload_url = blobstore.create_upload_url('/spudderadmin/leagueathletics')
    error_message = None

    la_import = LeagueAthleticsImport.load()
    import_form = LeagueAthleticsImportClubsForm(initial={'action': LeagueAthleticsFormAction.IMPORT_CLUBS})
    reset_form = LeagueAthleticsResetClubsForm(initial={'action': LeagueAthleticsFormAction.RESET_CLUBS})

    if request.method == "POST":
        action = request.POST.get('action')

        if action == LeagueAthleticsFormAction.IMPORT_CLUBS:
            import_form = LeagueAthleticsImportClubsForm(request.POST)

            if import_form.is_valid():
                upload_form = UploadForm(request.POST, request.FILES)
                uploaded_file = upload_form.save(False)
                uploaded_file.owner = request.user
                uploaded_file.content_type = request.FILES['file'].content_type
                uploaded_file.filename = request.FILES['file'].name
                uploaded_file.save()

                la_import.clear()
                la_import.in_progress = True
                la_import.zip_codes_file = uploaded_file
                la_import.save()

                trigger_backend_task('/spudderadmin/leagueathletics/import_clubs',
                                     eta=datetime.datetime.now() + datetime.timedelta(seconds=30))

                messages.success(request, "<i class='fa fa-check'></i> Clubs import in progress")

                return redirect('/spudderadmin/leagueathletics')

        if action == LeagueAthleticsFormAction.RESET_CLUBS:
            reset_form = LeagueAthleticsResetClubsForm(request.POST)
            if reset_form.is_valid():
                Club.objects.filter(original_domain_name='leagueathletics').delete()

                messages.success(request, "<i class='fa fa-check'></i> All imported clubs have been deleted")

                return redirect('/spudderadmin/leagueathletics')

    return render(request, 'spudderadmin/pages/leagueathletics/dashboard.html', {
        'imported_clubs_count': imported_clubs_count,
        'upload_url': upload_url,
        'error_message': error_message,
        'la_import': la_import,
        'reset_form': reset_form,
        'import_form': import_form
    })


@require_POST
def import_clubs(_):
    la_import = LeagueAthleticsImport.load()

    try:
        reader = blobstore.BlobReader(la_import.zip_codes_file.file.file.blobstore_info)

        current_line = 0
        for row in reader:
            current_line += 1

            if la_import.current_line > 0 and la_import.current_line >= current_line:
                logging.info('Omitting line %s' % current_line)
                # If import task was resumed at some time we don't want to process same lines again
                continue

            zip_code = row[:-1]
            programs = None
            if zip_code:
                programs = fetch_programs_for_zip(zip_code)

            imported_count = 0
            total_count = 0
            if programs:
                total_count = len(programs)
                for program in programs:
                    was_saved = save_club_from_program_json_data(program)
                    if was_saved:
                        imported_count += 1

            la_import.current_line = current_line
            la_import.update_progress(row)
            la_import.update_statistics(zip_code, total_count, imported_count)
            la_import.save()

            logging.info('-'*90)
            logging.info('Processed line %s (zip code: %s)' % (current_line, zip_code))
            logging.info('-'*90)
    except Exception:
        logging.error('Error occurred while importing Clubs from leagueathletics.com')
        logging.error(traceback.format_exc())

        return HttpResponseForbidden()  # postponing further execution of task

    la_import.in_progress = False
    la_import.save()

    return HttpResponse()


@admin_login_required
def import_statistics(request):
    la_import = LeagueAthleticsImport.load()

    return render_to_response('spudderadmin/pages/leagueathletics/import_statistics.html', {
        'la_import': la_import
    })


@admin_login_required
def list_imported_clubs(request):
    clubs = Club.objects.filter(original_domain_name='leagueathletics').order_by('name')

    paginator = EntitiesPaginator(clubs, 50)
    current_page = int(request.GET.get('page', 1))
    page = paginator.page(current_page)

    form = LeagueAthleticsImportedClubsSearchForm()
    if request.method == "POST":
        form = LeagueAthleticsImportedClubsSearchForm(request.POST)
        if form.is_valid():
            original_name = request.POST.get('name', None)
            if original_name:
                clubs = clubs.filter(name=original_name)

    paginator = EntitiesPaginator(clubs, 50)
    current_page = int(request.GET.get('page', 1))
    page = paginator.page(current_page)

    return render_to_response('spudderadmin/pages/leagueathletics/list_imported_clubs.html', {
        'clubs': page.object_list,
        'page': page,
        'total_pages': paginator.num_pages,
        'paginator_page': page.number,
        'start': page.start_index(),
        'search_form': form
    })