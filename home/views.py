from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
import pandas as pd
from sklearn.feature_extraction.text import TfidfTransformer
import numpy as np
from sklearn.linear_model import Ridge
from sklearn import linear_model
import math
from django.db import models
import json
from django.http import JsonResponse


url_user = 'C:/Users/TuanPham/Desktop/ml-100k/ml-100k/u.user'  # link file users
url_item = 'C:/Users/TuanPham/Desktop/ml-100k/ml-100k/u.item'  # link file item
url_rate = 'C:/Users/TuanPham/Desktop/ml-100k/ml-100k/ua.base'  # link file rate
cols_users = ['user_id', 'age', 'sex', 'gmail', 'zip_code']
cols_rate = ['user_id', 'movie_id', 'rating', 'unix_timestamp']


URL_DB = 'C:/Users/TuanPham/Desktop/ml-100k/ml-100k'
COLS_GENDERS_ITEM = ['movie id', 'movie title','release date', 'Img', 'IMDb URL', 'unknown', 'Action', 'Adventure', 'Animation',
                     'Children', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance',
                     'Sci-Fi', 'Thriller', 'War', 'Western']

# Create your views here.


def choose_algorithm(request):

    return render(request, 'pages/home.html')
    # return render(request, 'pages/base.html')

def ContentBased(request):
    return render(request, 'pages/base.html')


def recommend(request, user_id):    
 
    # code Recommend
    # nó sẽ truyền lên hàm này thay vì hàm search
  
     ra = Run_algorithm(user_id)
     json_object = dict(ra)
     return render (request,'pages/index.html',{'json_context': json_object})


def test_form(request, name_field): 
    pass

def search(request):
    if request.method == 'POST':
        try:
            email = request.POST["user"]
            user_id = convert_email_to_user_id(URL_DB, email)
            print("Email nay`: " + email + " co user_id = " + str(user_id))
            ra = Run_algorithm(user_id)
            json_object = dict(ra)
            # print(json_object['reference_5star'])
            return render(request, 'pages/index.html', {'json_context': json_object})
        except KeyError:
            return


def get_items_rated_by_user(rate_matrix, user_id):
    y = rate_matrix[:, 0]  # all users
    # item indices rated by user_id
    # we need to +1 to user_id since in the rate_matrix, id starts from 1
    # while index in python starts from 0
    ids = np.where(y == user_id + 1)[0]
    item_ids = rate_matrix[ids, 1] - 1  # index starts from 0
    scores = rate_matrix[ids, 2]
    return (item_ids, scores)

def convert_email_to_user_id(URL_DB, email):
    with open(URL_DB + '/u.user', 'r') as f:
        count = 0
        while count < 1000:
            line = f.readline()
            if len(line) != 0:
                line_data = line.split('|')
                if email in line_data[3]:
                    return int(line_data[0])
            count += 1

def Run_algorithm(user):
    # Load inf users
    cols_users = ['user_id', 'age', 'sex', 'gmail', 'zip_code']
    users = pd.read_csv(URL_DB + '/u.user', sep='|',
                        names=cols_users, encoding='latin-1')
    n_users = users.shape[0]
    # Load inf rate
    cols_rate = ['user_id', 'movie_id', 'rating', 'unix_timestamp']
    ratings_base = pd.read_csv(
        URL_DB + '/ua.base', sep='\t', names=cols_rate, encoding='latin-1')
    rate_train = ratings_base.as_matrix()
    # Load inf items
    items = pd.read_csv(URL_DB + '/u.item', sep='|',
                        names=COLS_GENDERS_ITEM, encoding='latin-1')
    n_items = items.shape[0]
    # Convert items into matrix
    X0 = items.as_matrix()
    X_train_counts = X0[:, -19:]  # only need 19 user reviews for items
    # tfidf
    transformer = TfidfTransformer(smooth_idf=True, norm='l2')
    tfidf = transformer.fit_transform(X_train_counts.tolist()).toarray()
    d = tfidf.shape[1]  # data dimension
    W = np.zeros((d, n_users))
    b = np.zeros((1, n_users))
    for n in range(n_users):
        ids, scores = get_items_rated_by_user(rate_train, n)
        clf = Ridge(alpha=0.01, fit_intercept=True)
        Xhat = tfidf[ids, :]
        clf.fit(Xhat, scores)
        W[:, n] = clf.coef_
        b[0, n] = clf.intercept_
    # điểm dự đoán 
    Yhat = tfidf.dot(W) + b
    
    # Lấy link từng bộ phim ↓  ↓ 
    url_5star = dict()
    url_4star = dict()
    url_3star = dict()
    # Lấy link từng bộ phim ↑  ↑ 
    
    date_5_star = dict()
    date_4_star = dict()
    date_3_star = dict()

      # Lấy hình ảnh  từng bộ phim ↓  ↓ 
    img_5star = dict()
    img_4star = dict()
    img_3star = dict()
     # Lấy hình ảnh  từng bộ phim ↑  ↑ 

    for i in range(n_items):
        if Yhat[i, user] >= 5:
            # Tui moi them vao
            title = items.iloc[i]['movie title']
            url = items.iloc[i]['IMDb URL']
            img = items.iloc[i]['Img']
            if isinstance(items.iloc[i]['release date'], str):
                date = items.iloc[i]['release date'][-4:]
                date_5_star[title] = int(date)
            img_5star[title] = img
            url_5star[title] = url
            # date_5_star[title] = int(date)

        elif (Yhat[i, user] >= 4 and Yhat[i, user] < 5):
            title = items.iloc[i]['movie title']
            url = items.iloc[i]['IMDb URL']
            img = items.iloc[i]['Img']
            if isinstance(items.iloc[i]['release date'], str):
                date = items.iloc[i]['release date'][-4:]
                date_4_star[title] = int(date)
            img_4star[title] = img
            url_4star[title] = url
            # date_4_star[title] = int(date)

        elif (Yhat[i, user] >= 3) and (Yhat[i, user] < 4):
            title = items.iloc[i]['movie title']
            url = items.iloc[i]['IMDb URL']
            img = items.iloc[i]['Img']
            print("debuggggggggggggggggggggggggggggggggggggggg")
            print(items.iloc[i]['release date'])
            print(type(items.iloc[i]['release date']))
            if isinstance(items.iloc[i]['release date'], str):
                date = items.iloc[i]['release date'][-4:]
                date_3_star[title] = int(date)
            img_3star[title] = img
            url_3star[title] = url
            # date_3_star[title] = int(date)
      

    return {
        # 'recommend_item_5start': recommend_item_5start[:5],
        # 'link' :  link_5start,
        # 'link' : link_5start,
        # 'three_start': recommend_item_3start[:5], 
        # 'four_start': recommend_item_4start[:5],
        'reference_5star': url_5star,
        'referenceImg_5star': img_5star,
        'reference_4star': url_4star,
        'referenceImg_4star': img_4star,
        'reference_3star': url_3star,
        'referenceImg_3star': img_3star,
        'referenceDate_5star': date_5_star,
        'referenceDate_4star': date_4_star,
        'referenceDate_3star': date_3_star,
       
    }
