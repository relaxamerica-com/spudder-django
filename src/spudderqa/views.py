from django.shortcuts import redirect, render
from spudderadmin.utils import encoded_admin_session_variable_name
from spudderqa.decorators import qa_login_required
from spudderqa.forms import QASigninForm


def signin(request):
    form = QASigninForm()
    if request.method == 'POST':
        form = QASigninForm(request.POST)
        if form.is_valid():
            request.session[encoded_admin_session_variable_name()] = True
            return redirect("/qa")
    return render(request, 'spudderqa/pages/signin.html', {'form': form})


@qa_login_required
def dashboard(request):
    return render(request, 'spudderqa/pages/dashboard.html')