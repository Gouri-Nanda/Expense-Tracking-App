from django.shortcuts import render
from django.http import JsonResponse
from bson.objectid import ObjectId
from decimal import Decimal
from django.shortcuts import redirect
from django.contrib import messages
from pymongo.errors import WriteError
from pymongo import MongoClient
import uuid
from datetime import datetime
# Import MongoClient and connect to MongoDB

client = MongoClient('mongodb://localhost:27017/')
db = client['expense_tracker']

# Function to render the index.html template
def index(request):
    # Retrieve user profile from MongoDB
    user_profile = db.userprofile.find_one()

    # Retrieve the most recently added debit and credit items from MongoDB
    debit = db.debit.find_one(sort=[('_id', -1)])
    credit = db.credit.find_one(sort=[('_id', -1)])

    # Render the index.html template with user profile, debit, and credit data
    return render(request, 'index.html', {'user_profile': user_profile, 'debit': debit, 'credit': credit})

# Function to edit user profile

def edit_user_profile(request):
    if request.method == 'POST':
        # Retrieve user profile data from the form
        name = request.POST.get('name')
        email = request.POST.get('email')
        gender = request.POST.get('gender')
        age = request.POST.get('age')
        amount = request.POST.get('amount')
        try:
            # Convert the amount value to a decimal
            amount = float(amount)
        except ValueError:
            return JsonResponse({'error': 'Invalid amount value'})


        # Update user profile in MongoDB
        user_profile = db.userprofile.find_one()
        if user_profile:
            try:
                result = db.userprofile.update_one({'_id': user_profile['_id']}, {'$set': {'name': name, 'email': email, 'gender': gender, 'age': age,'amount':amount}})
                if result.modified_count == 1:
                    return redirect('home')  # Redirect to the home page or the profile page
                else:
                    return redirect('home')
            except WriteError as e:
                if e.details.get('errmsg') == 'Document failed validation':
                    messages.error(request, 'Profile update failed due to validation error.')
                else:
                    messages.error(request, 'Profile update failed.')
        else:
            messages.error(request, 'User profile not found.') 

    # Render the edit_user_profile.html template
    return render(request, 'profile.html')





# Function to add an item to debit
def add_debit_item(request):
    if request.method == 'POST':
        # Retrieve debit item data from the form
        amount_str = request.POST.get('amount')
        category = request.POST.get('category')
        description = request.POST.get('description')

        try:
            # Convert the amount value to a decimal
            amount = float(amount_str)
        except ValueError:
            return JsonResponse({'error': 'Invalid amount value'})
        current_date = datetime.now().date().strftime('%Y-%m-%d')
        debit_item = {'id': str(uuid.uuid4()), 'amount': amount, 'category': category,'date':current_date}
        if description:
            debit_item['description'] = description

        # Insert debit item into MongoDB
        db.debit.insert_one(debit_item)

        user_profile = db.userprofile.find_one({})
        current_amount = user_profile.get('amount', 0)
        new_amount = current_amount - amount
        db.userprofile.update_one({}, {'$set': {'amount': new_amount}})

        return redirect('debit_info')
    return render(request, 'debit.html')


# Function to add an item to credit
def add_credit_item(request):
    if request.method == 'POST':
        # Retrieve credit item data from the form
        amount_str = request.POST.get('amount')
        category = request.POST.get('category')
        description = request.POST.get('description')


        try:
            # Convert the amount value to a decimal
            amount = float(amount_str)
        except ValueError:
            return JsonResponse({'error': 'Invalid amount value'})
        current_date = datetime.now().date().strftime('%Y-%m-%d')
        credit_item = {'id': str(uuid.uuid4()), 'amount': amount, 'category': category,'date': current_date}
        if description:
            credit_item['description'] = description

        # Insert credit item into MongoDB
        db.credit.insert_one(credit_item)

        user_profile = db.userprofile.find_one({})
        current_amount = user_profile.get('amount', 0)
        new_amount = current_amount + amount
        db.userprofile.update_one({}, {'$set': {'amount': new_amount}})

        return redirect('credit_info')  # Redirect to the home page
    return render(request, 'credit.html')
# Function to show items through filter
def show_filtered_items(request):
    filter_type = request.GET.get('filter_type')
    filter_value = request.GET.get('filter_value')

    debits = list(db.debit.find())  # Fetch all debit items
    if filter_type=='all':
        filtered_debits = debits

    elif filter_type == 'category' and filter_value:
        filtered_debits = list(db.debit.find({'category': filter_value}))
    else:
        filtered_debits = debits  # Define filtered_debits as an empty list

    return render(request, 'debit_info.html', {'filtered_debits': filtered_debits, 'debits': debits})


# Function to show summary of expenses

def summary_view(request):
    categories = set(db.debit.distinct('category'))

    total_spent_per_category = {}
    for category in categories:
        total_debits = list(db.debit.aggregate([{'$match': {'category': category}}, {'$group': {'_id': None, 'total_amount': {'$sum': '$amount'}}}]))
        total_credits = list(db.credit.aggregate([{'$match': {'category': category}}, {'$group': {'_id': None, 'total_amount': {'$sum': '$amount'}}}]))
        
        total_spent = (total_debits[0]['total_amount'] if total_debits else 0) - (total_credits[0]['total_amount'] if total_credits else 0)
        total_spent_per_category[category] = total_spent

    max_spent_category = None
    max_spent_amount = float('-inf')
    for category in categories:
        total_spent = list(db.debit.aggregate([{'$match': {'category': category}}, {'$group': {'_id': None, 'total_amount': {'$sum': '$amount'}}}]))
        try:
            total_spent_amount = total_spent[0]['total_amount']
        except IndexError:
            total_spent_amount = 0
        if total_spent_amount > max_spent_amount:
            max_spent_amount = total_spent_amount
            max_spent_category = category

    min_spent_category = None
    min_spent_amount = float('inf')
    for category in categories:
        total_spent = list(db.debit.aggregate([{'$match': {'category': category}}, {'$group': {'_id': None, 'total_amount': {'$sum': '$amount'}}}]))
        try:
            total_spent_amount = total_spent[0]['total_amount']
        except IndexError:
            total_spent_amount = 0
        if total_spent_amount < min_spent_amount:
            min_spent_amount = total_spent_amount
            min_spent_category = category

    total_debit = db.debit.aggregate([
        {'$group': {'_id': None, 'total_amount': {'$sum': '$amount'}}}
    ])
    try:
        total_debit_amount = total_debit.next()['total_amount']
    except StopIteration:
        total_debit_amount = 0

    total_credit = db.credit.aggregate([
        {'$group': {'_id': None, 'total_amount': {'$sum': '$amount'}}}
    ])
    try:
        total_credit_amount = total_credit.next()['total_amount']
    except StopIteration:
        total_credit_amount = 0

    return render(request, 'summary.html', {
        'total_debit': total_debit_amount, 'total_credit': total_credit_amount,
        'total_spent_per_category': total_spent_per_category,
        'max_spent_category': max_spent_category, 'max_spent_amount': max_spent_amount,
        'min_spent_category': min_spent_category, 'min_spent_amount': min_spent_amount
    })


#function tom delete debit
def delete_debit_item(request, debit_id):
    debit_item = db.debit.find_one({'id': debit_id})
    if debit_item:
        amount = debit_item.get('amount', 0)

        # Delete the debit item from MongoDB
        db.debit.delete_one({'id': debit_id})

        # Update UserProfile amount
        user_profile = db.userprofile.find_one({})
        current_amount = user_profile.get('amount', 0)
        new_amount = current_amount + amount
        db.userprofile.update_one({}, {'$set': {'amount': new_amount}})

        return redirect('debit_info')
    else:
        return JsonResponse({'error': 'Debit item not found'})

#function to delete credit
def delete_credit_item(request, credit_id):
    # Find the credit item and retrieve its amount
    credit_item = db.credit.find_one({'id': credit_id})
    if credit_item:
        amount = credit_item.get('amount', 0)

        # Delete the credit item from MongoDB
        db.credit.delete_one({'id': credit_id})

        # Update UserProfile amount
        user_profile = db.userprofile.find_one({})
        current_amount = user_profile.get('amount', 0)
        new_amount = current_amount - amount
        db.userprofile.update_one({}, {'$set': {'amount': new_amount}})

        return redirect('credit_info')
    else:
        return JsonResponse({'error': 'Credit item not found'})
    
#function to search credit
def show_search_items(request):
    filter_type = request.GET.get('filter_type')
    filter_value = request.GET.get('filter_value')

    credits = list(db.credit.find())  # Fetch all credit items
    if filter_type == 'category':
        if filter_value !=None:
            regex_query = {'category': {'$regex': filter_value, '$options': 'i'}}  # Case-insensitive regex search
            filtered_credits = list(db.credit.find(regex_query))
        else:
            filtered_credits = []
    elif filter_type == 'all' or filter_type == None:
        filtered_credits = credits
    else:
        filtered_credits = []  # Show all credit items if no filter is applied

    return render(request, 'credit_info.html', {'filtered_credits': filtered_credits, 'credits': credits})

