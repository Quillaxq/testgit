# -*- coding:utf-8 -*-
from django.shortcuts import render, HttpResponse, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, InvalidPage
from django.views.decorators.csrf import csrf_exempt
from user.models import users
import pymysql
import datetime


def all(request):
    return render(request, 'all.html')


def base(request):
    return render(request, 'index.html')


def movieinformation(request):
    return render(request, 'movie_information.html')


def login(request):
    res = ""
    if request.method == "POST":
        user = request.POST.get("userid")
        pwd = request.POST.get("userpasswd")
        user_obj = users.objects.filter(userid=user, userpasswd=pwd).first()
        if user_obj:
            """
            如果验证通过，则设置session,并返回index
            """
            request.session["is_login"] = True
            request.session["username"] = user_obj.username
            request.session['userid'] = user_obj.pk
            request.session.set_expiry(60 * 60 * 24 * 14)  # 设置过期时间
            obj = redirect("/index/")
            return obj
        else:
            res = "用户名或密码错误"
    return render(request, "login.html", {"res": res})


def index(request):
    is_login = request.session.get("is_login")
    username = request.session.get("username")
    if not is_login:
        """
        如果没有登录则跳转至登录页面
        """
        return redirect("/login/")
    return render(request, "index.html", {"user": username})


def logout(request):
    request.session.flush()
    return redirect("/login/")


def register(request):
    now = datetime.datetime.now()
    if request.method == 'POST':
        res = {}
        if 'reg2' in request.POST:  # 处理表单中的注册
            userid = request.POST['userid']
            username = request.POST['username']
            userpwd = request.POST['userpasswd']
            temp = users.objects.filter(userid=userid).exists()
            if temp:  # 若数据库中存在该用户名相关数据
                res['rlt'] = '该账号已被注册'
                return render(request, 'register.html', res)
            else:  # 用户未注册，则插入用户注册数据
                users.objects.create(userid=userid, userpasswd=userpwd, username=username,
                                     register_time=now.strftime("%Y-%m-%d,%H:%M:%S"))
                res['rlt'] = '注册成功'
                return render(request, 'register.html', res)
        else:
            pass
    return render(request, 'register.html')


def analyze(request):
    connection = pymysql.connect(host='121.89.219.177', port=3306, user='root', passwd='123456', db='bigdata')
    cursor = connection.cursor()
    movie_year = []
    movie_year_count = []
    movie_name = []
    movie_rate = []
    rating = []
    rating_count = []
    movie_china_year = []
    movie_china_year_count = []
    # select title,rating_num from moviedata having rating_num>9.3 order by rating_num desc;(评分>9.3的电影)
    # select count(year) from moviedata where country="中国大陆" order by count desc;
    cursor.execute('select title,rating_num from moviedata order by rating_num desc limit 2,12;')  # 评分前十的电影
    rows = cursor.fetchall()
    cursor.execute('select year,count(year) as count from moviedata group by year having year>=2010 order by year asc;')
    rows1 = cursor.fetchall()
    cursor.execute(
        'select rating_num,count(rating_num) as count from moviedata group by rating_num order by rating_num asc limit 1,74;')
    rows2 = cursor.fetchall()
    cursor.execute(
        "select year,count(year) as count from moviedata where country like '%中国%' group by year order by year asc;")  # 中国电影逐年统计
    rows3 = cursor.fetchall()

    for row in range(len(rows)):
        a = lambda x: x[row][0]
        b = lambda x: x[row][1]
        movie_name.append(a(rows))
        movie_rate.append(float(b(rows)))

    for row in range(len(rows1)):
        a = lambda x: x[row][0]
        b = lambda x: x[row][1]
        movie_year.append(a(rows1))
        movie_year_count.append(int(b(rows1)))

    for row in range(len(rows2)):
        a = lambda x: x[row][0]
        b = lambda x: x[row][1]
        rating.append(float(a(rows2)))
        rating_count.append(int(b(rows2)))

    for row in range(len(rows3)):
        a = lambda x: x[row][0]
        b = lambda x: x[row][1]
        movie_china_year.append(int(a(rows3)))
        movie_china_year_count.append(int(b(rows3)))

    return render(request, 'analyse_data.html',
                  {"movie_name": movie_name, "movie_rate": movie_rate, "movie_year": movie_year,
                   "movie_year_count": movie_year_count, "rating": rating, "rating_count": rating_count,
                   "movie_china_year": movie_china_year, "movie_china_year_count": movie_china_year_count})


def pages(request):
    connection = pymysql.connect(host='121.89.219.177', port=3306, user='root', passwd='123456', db='bigdata')
    cursor = connection.cursor()
    movie_information = []
    cursor.execute('select title,director,casts,rating_num,language,country,type,year,image from moviedata;')
    rows = cursor.fetchall()
    for row in range(1, len(rows)):
        a = lambda x: x[row]
        movie_information.append(a(rows))
    paginator = Paginator(movie_information, 10)
    if request.method == 'GET':
        page = request.GET.get('page')
        try:
            informations = paginator.page(page)
        except PageNotAnInteger:
            informations = paginator.page(1)
        except InvalidPage:
            return HttpResponse('找不到页面的内容')
        except EmptyPage:
            informations = paginator.page(paginator.num_pages)

    return render(request, 'movie_show.html', {'movie_informations': informations})


def search(request):
    connection = pymysql.connect(host='121.89.219.177', port=3306, user='root', passwd='123456', db='bigdata')
    cursor = connection.cursor()
    if request.method == 'POST':
        if 'search' in request.POST:  # 处理表单中的搜索
            keyword = request.POST['keyword']
            keyword = "%" + keyword + "%"
            movie_information = []
            temp = "select title,director,casts,rating_num,language,country,type,year,image from moviedata where director like '{}' or title like '{}' or casts like '{}' or rating_num like '{}'or language like '{}' or country like '{}' or type like '{}' or year like '{}';".format(
                keyword, keyword, keyword, keyword, keyword, keyword, keyword, keyword)
            if cursor.execute(temp):
                is_reg = cursor.fetchall()
                if is_reg != None:  # 查询有结果，返回电影信息
                    rows = is_reg
                    for row in range(len(rows)):
                        a = lambda x: x[row]
                        movie_information.append(a(rows))
                    return render(request, 'search.html', {'movie_informations': movie_information})
                else:  # 查询无结果，提示出错
                    return HttpResponse('查询无结果')
            else:
                pass
        else:
            pass
    return render(request, 'search.html')



@csrf_exempt
def classify(request):
    connection = pymysql.connect(host='121.89.219.177', port=3306, user='root', passwd='123456', db='bigdata')
    cursor = connection.cursor()
    movie_information = []
    if request.method == 'POST':
        if 'comedy' in request.POST:  # 处理表单中的登录
            cursor.execute(
                "select title,director,casts,rating_num,language,country,type,year,image from moviedata where type like '%喜剧%';")
            rows = cursor.fetchall()
            if rows != None:  # 查询有结果，返回电影信息
                for row in range(len(rows)):
                    a = lambda x: x[row]
                    movie_information.append(a(rows))
                return render(request, 'classify.html', {'movie_informations': movie_information})
            else:  # 查询无结果，提示出错
                return HttpResponse('查询无结果')
        elif 'amor' in request.POST:
            cursor.execute(
                "select title,director,casts,rating_num,language,country,type,year,image from moviedata where type like '%爱情%';")
            rows = cursor.fetchall()
            if rows != None:  # 查询有结果，返回电影信息
                for row in range(len(rows)):
                    a = lambda x: x[row]
                    movie_information.append(a(rows))
                return render(request, 'classify.html', {'movie_informations': movie_information})
            else:  # 查询无结果，提示出错
                return HttpResponse('查询无结果')
        elif 'action' in request.POST:
            cursor.execute(
                "select title,director,casts,rating_num,language,country,type,year,image from moviedata where type like '%动作%';")
            rows = cursor.fetchall()
            if rows != None:  # 查询有结果，返回电影信息
                for row in range(len(rows)):
                    a = lambda x: x[row]
                    movie_information.append(a(rows))
                return render(request, 'classify.html', {'movie_informations': movie_information})
            else:  # 查询无结果，提示出错
                return HttpResponse('查询无结果')
        elif 'suspe' in request.POST:
            cursor.execute(
                "select title,director,casts,rating_num,language,country,type,year,image from moviedata where type like '%悬疑%';")
            rows = cursor.fetchall()
            if rows != None:  # 查询有结果，返回电影信息
                for row in range(len(rows)):
                    a = lambda x: x[row]
                    movie_information.append(a(rows))
                return render(request, 'classify.html', {'movie_informations': movie_information})
            else:  # 查询无结果，提示出错
                return HttpResponse('查询无结果')
        elif 'elsetype' in request.POST:
            cursor.execute(
                "select title,director,casts,rating_num,language,country,type,year,image from moviedata where type not like '%爱情%' and type not like '%喜剧%' and type not like '%动作%' and type not like '%悬疑%';")
            rows = cursor.fetchall()
            if rows != None:  # 查询有结果，返回电影信息
                for row in range(len(rows)):
                    a = lambda x: x[row]
                    movie_information.append(a(rows))
                return render(request, 'classify.html', {'movie_informations': movie_information})
            else:  # 查询无结果，提示出错
                return HttpResponse('查询无结果')
        elif 'Chinese' in request.POST:  # 处理表单中的登录
            cursor.execute(
                "select title,director,casts,rating_num,language,country,type,year,image from moviedata where country like '%中国大陆%';")
            rows = cursor.fetchall()
            if rows != None:  # 查询有结果，返回电影信息
                for row in range(len(rows)):
                    a = lambda x: x[row]
                    movie_information.append(a(rows))
                return render(request, 'classify.html', {'movie_informations': movie_information})
            else:  # 查询无结果，提示出错
                return HttpResponse('查询无结果')
        elif 'HK' in request.POST:
            cursor.execute(
                "select title,director,casts,rating_num,language,country,type,year,image from moviedata where country like '%中国香港%';")
            rows = cursor.fetchall()
            if rows != None:  # 查询有结果，返回电影信息
                for row in range(len(rows)):
                    a = lambda x: x[row]
                    movie_information.append(a(rows))
                return render(request, 'classify.html', {'movie_informations': movie_information})
            else:  # 查询无结果，提示出错
                return HttpResponse('查询无结果')
        elif 'US' in request.POST:
            cursor.execute(
                "select title,director,casts,rating_num,language,country,type,year,image from moviedata where country like '%美国%';")
            rows = cursor.fetchall()
            if rows != None:  # 查询有结果，返回电影信息
                for row in range(len(rows)):
                    a = lambda x: x[row]
                    movie_information.append(a(rows))
                return render(request, 'classify.html', {'movie_informations': movie_information})
            else:  # 查询无结果，提示出错
                return HttpResponse('查询无结果')
        elif 'Korea' in request.POST:
            cursor.execute(
                "select title,director,casts,rating_num,language,country,type,year,image from moviedata where country like '%韩国%';")
            rows = cursor.fetchall()
            if rows != None:  # 查询有结果，返回电影信息
                for row in range(len(rows)):
                    a = lambda x: x[row]
                    movie_information.append(a(rows))
                return render(request, 'classify.html', {'movie_informations': movie_information})
            else:  # 查询无结果，提示出错
                return HttpResponse('查询无结果')
        elif 'elsecountry' in request.POST:
            cursor.execute(
                "select title,director,casts,rating_num,language,country,type,year,image from moviedata where country not like '%中国大陆%' and country not like '%中国香港%' and country not like '%美国%' and country not like '%韩国%';")
            rows = cursor.fetchall()
            if rows != None:  # 查询有结果，返回电影信息
                for row in range(len(rows)):
                    a = lambda x: x[row]
                    movie_information.append(a(rows))
                return render(request, 'classify.html', {'movie_informations': movie_information})
            else:  # 查询无结果，提示出错
                return HttpResponse('查询无结果')
        elif 'newest' in request.POST:
            cursor.execute(
                "select title,director,casts,rating_num,language,country,type,year,image from moviedata where year>=2022 order by year desc;")
            rows = cursor.fetchall()
            if rows != None:  # 查询有结果，返回电影信息
                for row in range(len(rows)):
                    a = lambda x: x[row]
                    movie_information.append(a(rows))
                return render(request, 'classify.html', {'movie_informations': movie_information})
            else:  # 查询无结果，提示出错
                return HttpResponse('查询无结果')
        elif 'gradest' in request.POST:
            cursor.execute(
                "select title,director,casts,rating_num,language,country,type,year,image from moviedata where rating_num>=9 order by rating_num desc limit 0,19;")
            rows = cursor.fetchall()
            if rows != None:  # 查询有结果，返回电影信息
                for row in range(len(rows)):
                    a = lambda x: x[row]
                    movie_information.append(a(rows))
                return render(request, 'classify.html', {'movie_informations': movie_information})
            else:  # 查询无结果，提示出错
                return HttpResponse('查询无结果')
    return render(request, 'classify.html')

