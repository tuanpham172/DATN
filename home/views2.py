from __future__ import print_function
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy import sparse
from django.db import models
import json
from django.http import JsonResponse
url_user = 'C:/Users/TuanPham/Desktop/ml-100k/ml-100k/u.user'  # link file users
url_item = 'C:/Users/TuanPham/Desktop/ml-100k/ml-100k/u.item'  # link file item
url_rate = 'C:/Users/TuanPham/Desktop/ml-100k/ml-100k/ua.base'  # link file rate


URL_DB = 'C:/Users/TuanPham/Desktop/ml-100k/ml-100k'
cols_genders_item = ['movie id', 'movie title', 'release date', 'Img', 'IMDb URL', 'unknown', 'Action', 'Adventure', 'Animation',
                     'Children', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance',
                     'Sci-Fi', 'Thriller', 'War', 'Western']
cols_users = ['user_id', 'age', 'sex', 'occupation', 'zip_code']
cols_rate = ['user_id', 'movie_id', 'rating', 'unix_timestamp']


# Create your views here.
def choose_algorithm(request):
    return render(request, 'pages/home.html')

def NeighborhoodBased(request):
    return render(request, 'pages/base2.html')


def recommendItemByUser(request):
    if request.method == 'POST':
        try:
            email = request.POST["user_id"]
            user_id = convert_email_to_user_id(URL_DB, email)
            print("Email nay`: " + email + " co user_id = " + str(user_id))
            ra = Run_algorithm1(user_id)
            json_object = dict(ra)
            # print(json_object['reference_5star'])
            return render(request, 'pages/indexUser.html', {'json_context': json_object})
        except KeyError:
            return
    # code Recommend
    # ra = Run_algorithm1(user_id)
    # json_object = dict(ra)
    # return render(request, 'pages/index.html', {'json_context': json_object})
    
def recommendItemByItem(request ):
    # code Recommend
    # ra2 = Run_algorithm2(user_id)
    # json_object = dict(ra2)
    # return render(request, 'pages/index2.html', {'json_context': json_object})
    if request.method == 'POST':
        try:
            email = request.POST["user_id2"]
            user_id = convert_email_to_user_id(URL_DB, email)
            print("Email nay`: " + email + " co user_id = " + str(user_id))
            ra = Run_algorithm2(user_id)
            json_object = dict(ra)
            # print(json_object['reference_5star'])
            return render(request, 'pages/indexItem.html', {'json_context': json_object})
        except KeyError:
            return
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


class Neighborhood_Based(object):
    """docstring for NB"""

    def __init__(self, Y_data, k, dist_func=cosine_similarity, uuCF=1):
        self.uuCF = uuCF  # user-user (1) hoac item-item (0) CF 
        self.Y_data = Y_data if uuCF else Y_data[:, [1, 0, 2]]
        self.k = k  
        self.dist_func = dist_func
        self.Ybar_data = None
        # number of users and items. Remember to add 1 since id starts from 0
        # so luon cua user va item . Can add 1 vao vi id bat dau tu 0
        self.n_users = int(np.max(self.Y_data[:, 0])) + 1
        self.n_items = int(np.max(self.Y_data[:, 1])) + 1

    def add(self, new_data):
        """
        Update Y_data matrix when new ratings come.
        For simplicity, suppose that there is no new user or item.
        """
        self.Y_data = np.concatenate((self.Y_data, new_data), axis=0)

    def normalize_Y(self):
        users = self.Y_data[:, 0]  # tat ca user- cot dau tien cua Y-data
        self.Ybar_data = self.Y_data.copy()
        self.mu = np.zeros((self.n_users,))
        for n in range(self.n_users):
          
            ids = np.where(users == n)[0].astype(np.int32)
       
            item_ids = self.Y_data[ids, 1]
       
            ratings = self.Y_data[ids, 2]
          
            m = np.mean(ratings)
            self.mu[n] = m
            if np.isnan(m):
                m = 0  
            # normalize
            self.Ybar_data[ids, 2] = ratings - self.mu[n]

     
        self.Ybar = sparse.coo_matrix((self.Ybar_data[:, 2],
                                       (self.Ybar_data[:, 1], self.Ybar_data[:, 0])), (self.n_items, self.n_users))
        self.Ybar = self.Ybar.tocsr()

    def similarity(self):
        self.S = self.dist_func(self.Ybar.T, self.Ybar.T)

    def refresh(self):
        """
        Normalize data and calculate similarity matrix again (after
        some few ratings added)
        """
        self.normalize_Y()
        self.similarity()

    def fit(self):
        self.refresh()

    def __pred(self, u, i, normalized=1):

        # Buoc 1 : Tim tat ca user da rate cho i
        ids = np.where(self.Y_data[:, 1] == i)[0].astype(np.int32)
        # Buoc 2:
        users_rated_i = (self.Y_data[ids, 0]).astype(np.int32)
        # Buoc 3: Tim do giong nhau giua cac user hien tai 
        # da rate cho i
        sim = self.S[u, users_rated_i]
        # Step 4: Tim do giong nhau lon naht
        a = np.argsort(sim)[-self.k:]
       
        nearest_s = sim[a]
     
        r = self.Ybar[i, users_rated_i[a]]

        return (r*nearest_s)[0]/(np.abs(nearest_s).sum() + 1e-8) + self.mu[u]

    def pred(self, u, i, normalized=1):
     
        if self.uuCF:
            return self.__pred(u, i, normalized)
        return self.__pred(i, u, normalized)

    def recommend(self,items, user_id, normalized=1):
     
       
        url_5star = dict()
        url_4star = dict()
        url_3star = dict()

        img_5star = dict()
        img_4star = dict()
        img_3star = dict()

            
        date_5_star = dict()
        date_4_star = dict()
        date_3_star = dict()

        ids = np.where(self.Y_data[:, 0] == 0)[0]
        # user = int(input("moi nhap vao user"))
        items_rated_by_u = self.Y_data[ids, 1].tolist()
        for i in range(self.n_items):
            if i not in items_rated_by_u:
                rating = self.__pred(int(user_id), i)
                if rating >= 4.5:
                     title = items.iloc[i]['movie title']
                     url = items.iloc[i]['IMDb URL']
                     img = items.iloc[i]['Img']
                     if isinstance(items.iloc[i]['release date'], str):
                         date = items.iloc[i]['release date'][-4:]
                         date_5_star[title] = int(date)
                 
                     url_5star[title] = url
                     img_5star[title] = img
                    #  date_5_star[title] = int(date)
                    # recommend_item_5start.append(items.iloc[i]['movie title'])
                    # five_start += 1
                elif (rating >= 3.5 and rating < 4.5):
                     title = items.iloc[i]['movie title']
                     url = items.iloc[i]['IMDb URL']
                     img = items.iloc[i]['Img']
                     if isinstance(items.iloc[i]['release date'], str):
                         date = items.iloc[i]['release date'][-4:]
                         date_4_star[title] = int(date)
                     url_4star[title] = url
                     img_4star[title] = img
                    #  date_4_star[title] = int(date)
                    # four_start += 1
                    # recommend_item_4start.append(items.iloc[i]['movie title'])
                elif (rating >= 2.5) and (rating < 3.5):
                     title = items.iloc[i]['movie title']
                     url = items.iloc[i]['IMDb URL']
                     img = items.iloc[i]['Img']
                     if isinstance(items.iloc[i]['release date'], str):
                         date = items.iloc[i]['release date'][-4:]
                         date_3_star[title] = int(date)
                     url_3star[title] = url
                     img_3star[title] = img
                    #  date_3_star[title] = int(date)
                    # three_start += 1
                    # recommend_item_3start.append(items.iloc[i]['movie title'])

        # print("Khuyến nghị sản phẩm 5 sao :", recommend_item_5start, "cho users 0")
        # print("Số phim đạt 3 sao đến dưới 4 sao :", three_start)
        # print("Số phim đạt 4 sao đến dưới 5 sao:", four_start)
        # print("Số phim đạt 5 sao trở lên :", five_start)
        return{
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


def Run_algorithm1(user):
    # Load inf users
    cols_users = ['user_id', 'age', 'sex', 'occupation', 'zip_code']
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
                        names=cols_genders_item, encoding='latin-1')
    n_items = items.shape[0]
    # run
    rate_train = ratings_base.as_matrix()
    # indices start from 0
    rate_train[:, :2] -= 1
    rs = Neighborhood_Based(rate_train, k=30, uuCF=1)
    rs.fit()
    return rs.recommend(items, user)
def Run_algorithm2(user):
    #Load inf users
    cols_users =  ['user_id', 'age', 'sex', 'occupation', 'zip_code']
    users = pd.read_csv(URL_DB + '/u.user', sep='|', names=cols_users,encoding='latin-1')
    n_users = users.shape[0]
    #Load inf rate
    cols_rate = ['user_id', 'movie_id', 'rating', 'unix_timestamp']
    ratings_base = pd.read_csv(URL_DB + '/ua.base', sep='\t', names=cols_rate, encoding='latin-1')
    rate_train = ratings_base.as_matrix()
    #Load inf items
    items = pd.read_csv(URL_DB + '/u.item', sep='|', names=cols_genders_item,encoding='latin-1')
    n_items = items.shape[0]
    #run   
    rate_train = ratings_base.as_matrix()
    # indices start from 0
    rate_train[:, :2] -= 1
    rs = Neighborhood_Based(rate_train, k = 30, uuCF = 0)
    rs.fit()
    return rs.recommend(items, user)
