"""
URL configuration for expense_tracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from expense.views import index, edit_user_profile, add_debit_item, add_credit_item, show_filtered_items,summary_view, delete_debit_item, delete_credit_item, show_search_items

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='home'),
    path('edit_user_profile/', edit_user_profile, name='edit_user_profile'),
    path('add_debit_item/', add_debit_item, name='add_debit_item'),
    path('add_credit_item/', add_credit_item, name='add_credit_item'),
    path('delete_debit_item/<str:debit_id>/', delete_debit_item, name='delete_debit_item'),
    path('delete_credit_item/<str:credit_id>/', delete_credit_item, name='delete_credit_item'),
    path('summary/', summary_view, name='summary'),
    path('credit_info/', show_search_items, name='credit_info'),
    path('debit_info/',show_filtered_items, name='debit_info'),
]
