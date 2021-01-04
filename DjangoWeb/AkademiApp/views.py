import datetime
from django.shortcuts import render, HttpResponse, redirect, HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.cache import cache
import traceback,random
#from AkademiWeb.settings import db, auth, db_storage, DEBUG
from google.cloud import firestore



def AnaSayfa(request):
    return render(request, 'Ayarlar.html')

def girisSayfasi(request):
    if auth.current_user is not None:
        return render(request, 'Anasayfa.html', {})
    else:
        if request.method == 'POST':
            user_email = request.POST['input_KullaniciEmail']
            user_password = request.POST['input_KullaniciSifresi']
            try:
                auth.current_user = auth.sign_in_with_email_and_password(email=user_email, password=user_password)
                logged_user_id = auth.current_user['localId']
                request.session['email'] = auth.current_user['email']
                request.session['id'] = auth.current_user['localId']

                user_data = db.collection(u'userData').document(u'{}'.format(logged_user_id)).get()
                user_account_data = user_data.to_dict()

                # Kullanıcının mevcut verileri önbelleğe atanır:
                avatar = db_storage.child('Avatar/{}'.format(user_account_data['userAvatar'])).get_url("")
                request.session['avatar'] = avatar

                return redirect('anasayfa')

            except Exception as error:
                if DEBUG:
                    traceback.print_exc()
                return render(request, 'GirisSayfasi.html', {'CVP': 'FALSE'})
        else:
            return render(request, 'GirisSayfasi.html', {})


def anasayfa(request):
    if auth.current_user is not None:
        doc_ref = db.collection(u'userData').document(u'{}'.format(request.session['id'])).get()
        doc = doc_ref.to_dict()
        request.session['username'] = doc['userFullname']

        room_a_ref = db.collection(u'userData').document(u'{}'.format(request.session['id'])).collection(
            u'statics').document(u'statics').get()
        lesson_data = room_a_ref.to_dict()
        request.session['lesson'] = lesson_data['complated_lessons']

        user_statistics = db.collection(u'userData').document(u'{}'.format(request.session['id'])).collection(
            u'statics').document(u'statics').get()
        user_tutorials = db.collection(u'userData').document(u'{}'.format(request.session['id'])).collection(
            u'tutorials').stream()

        user_data = db.collection(u'userData').document(u'{}'.format(request.session['id'])).get()
        user_account_data = user_data.to_dict()
        avatar = db_storage.child('Avatar/{}'.format(user_account_data['userAvatar'])).get_url("")

        return render(request, 'Anasayfa.html', {'EgitimData': user_tutorials,'user_data':doc, 'user_stat':user_statistics.to_dict(),'avatar':avatar})
    else:
        if DEBUG:
            traceback.print_exc()
        return redirect('girisSayfasi')


def kullaniciCikis(request):
    if auth.current_user is not None:
        request.session['username'] = None
        request.session['id'] = None
        auth.current_user = None
        return redirect('girisSayfasi')
    else:
        return redirect('girisSayfasi')



def forum(request):
    #if auth.current_user is not None:

    forum_topics = db.collection(u'Forum').limit(12).get()
    user_ids = []
    for item in forum_topics:
        user_ids.append(item.to_dict()['user'])

    forum_avatars = []
    while user_ids:
        commentor_profile = db.collection(u'userData').document(u'{}'.format(user_ids[0])).get()
        commenter_avatar = db_storage.child('Avatar/{}'.format(commentor_profile.to_dict()['userAvatar'])).get_url("")
        forum_avatars.append(commenter_avatar)
        user_ids.pop(0)

    forum_data = db.collection(u'Forum').limit(12).get()
    #Tarihe göre çekmesi ayarlanabilir.

    return render(request,'Forum.html',{'forum_topic':forum_data,'forum_avatar':forum_avatars})
    #else:
    #    return redirect('girisSayfasi')

def forumIcerik(request,forum_name):
    if auth.current_user is not None:
        commenter = db.collection(u'userData').document(u'{}'.format(auth.current_user['localId'])).get()
        if request.method == 'POST':
            print("method Post")
            yorum = request.POST['yorum']
            try:
                print("Try ettim")
                data = {
                    u'detail':yorum,
                    u'date':datetime.datetime.now(),
                    u'userName':commenter.to_dict()['userFullname'],
                    u'user':auth.current_user['localId']
                }

                to_comment = db.collection(u'Forum').document(u'{}'.format(forum_name))
                comment = to_comment.collection(u'comments').document()
                comment.set(data)

            except Exception as err:
                print(err)
        yorumAvatars = []
        comment_avatars = db.collection(u'Forum').document(u'{}'.format(forum_name)).collection(
            u'comments').order_by('date').get() # yorumları tarihe göre çektik.

        for item in comment_avatars:
            commentor_profile = db.collection(u'userData').document(u'{}'.format(item.to_dict()['user'])).get()
            commenter_avatar = db_storage.child('Avatar/{}'.format(commentor_profile.to_dict()['userAvatar'])).get_url("")
            yorumAvatars.append(commenter_avatar)


        forum_content = db.collection(u'Forum').document(u'{}'.format(forum_name)).collection(
            u'comments').order_by('date').stream()


        forum_data = db.collection(u'Forum').document(u'{}'.format(forum_name)).get()
        user_data = db.collection(u'userData').document(u'{}'.format(forum_data.to_dict()['user'])).get()

        avatar = db_storage.child('Avatar/{}'.format(user_data.to_dict()['userAvatar'])).get_url("") # Konu sahibinin avatarı çekildi.



        context = {'forum_content':forum_content, 'forum_name':forum_name, 'user_data':user_data,"topic_avatar":avatar,'forum_data':forum_data,'comment_avatar':yorumAvatars}

        return render(request,'ForumContent.html',context)
    else:
        return redirect('girisSayfasi')


def forumYeniKonu(request):
    if auth.current_user is not None:
        if request.method == "POST":
            return render(request, 'ForumYeniKonu.html', {})
        else:
            if DEBUG:
                traceback.print_exc()
            return render(request, 'ForumYeniKonu.html', {})
    else:
        return redirect('girisSayfasi')

def notDefteri(request):
  if auth.current_user is not None:
    return render(request, 'NotDefteri.html', {})
  else:
     return redirect('girisSayfasi')

def ayarlar(request):
  if auth.current_user is not None:
      data = db.collection(u'userData').document(u'{}'.format(request.session['id'])).get()
      return render(request, 'Ayarlar.html', {'userData':data})
  else:
     return redirect('girisSayfasi')


def kodYaz(request):
  if auth.current_user is not None:
    return render(request, 'KodYaz.html', {})
  else:
     return redirect('girisSayfasi')

def reset_password(request):
    if auth.current_user is not None:

        try:

            oldPassword = request.POST['oldPass']
            newPassword = request.POST['newPassword']
            newConfirmPassword = request.POST['con-password']

            print('OLD Pass => ' + oldPassword)
            print('NEW Pass =>' + newPassword)
            print('NEW CONFİRM Pass => ' + newConfirmPassword)
            request.session['email'] = ['email']
            request.session['id'] = ['localId']
            return render(request, 'sifreSifirlama.html', {'onay': 'TRUE'})
        except:
            if DEBUG:
                traceback.print_exc()
            return render(request, 'sifreSifirlama.html', {'onay': 'FALSE'})
    else:
        return redirect('girisSayfasi')



def other_profiles(request,otherUser):
    if auth.current_user is not None:
        user_data = db.collection(u'userData').document(u'{}'.format(otherUser)).get()
        user_account_data = user_data.to_dict()


        avatar = db_storage.child('Avatar/{}'.format(otherUser)).get_url("")
        user_statistics = db.collection(u'userData').document(u'{}'.format(otherUser)).collection(u'statics').document(u'statics').get()

        room_a_ref = db.collection(u'userData').document(u'{}'.format(otherUser)).collection(
            u'statics').document(u'statics').get()
        lesson_data = room_a_ref.to_dict()
        request.session['lesson'] = lesson_data['complated_lessons']


        user_tutorials = db.collection(u'userData').document(u'{}'.format(otherUser)).collection(
            u'tutorials').stream()

        if request.method == 'POST':
            if 'takipet' in request.POST:
                # OtherUser haricinde kendi bilgilerimizi de update etmeliyiz.
                user_to_follow = db.collection(u'userData').document(u'{}'.format(otherUser))

                user_to_follow.update(
                    {u'userFollowers': firestore.ArrayUnion([u'{}'.format(auth.current_user['localId'])])})


        return render(request, 'Anasayfa.html', {'EgitimData':user_tutorials,'user_data':user_account_data, 'user_stat': user_statistics.to_dict(), 'avatar':avatar})
    else:
        return redirect('girisSayfasi')



def news(request):
    if auth.current_user is not None:
        news_data = db.collection(u'News').limit(15).stream()

        return render(request, 'Bulten.html', {'newsData': news_data})
    else:
        return redirect('girisSayfasi')


def tutorial_dashboard(request):
    #if auth.current_user is not None:
    tutorial_names = db.collection(u'tutorial_data_browser').get()

    return render(request, 'Egitimler.html', {'lesson_names':tutorial_names})

    #else:
    #    return redirect('girisSayfasi')



def tutorial_detail(request,lesson_names):
    if auth.current_user is not None:
        global ders_ismi
        ders_ismi = lesson_names
        tutorial_sidebar = db.collection(u'tutorial_data_browser').document(u'{}'.format(ders_ismi)).collection(u'tutorial_lessons4').order_by(u'no').stream()

        about_tutorial = db.collection(u'tutorial_data_browser').document(u'{}'.format(ders_ismi)).get()

        author_data = db.collection(u'userData').document(u'{}'.format(about_tutorial.to_dict()['Authorid'])).get()

        author_avatar = db_storage.child('Avatar/{}'.format(author_data.to_dict()['userAvatar'])).get_url("")

        lst = [1,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,91,92,93,94,95,96,97,98,99,100]

        #if ders_ismi == "BeautifulSoup4":
        #    tutorial_avatar = db.collection(u'v2TutorialData').document(u'Python').get()
        #    avatar = db_storage.child('Avatar/{}'.format(tutorial_avatar.to_dict()['lessonAvatar'])).get_url("")
        #else:
        #    tutorial_avatar = db.collection(u'v2TutorialData').document(u'{}'.format(ders_ismi)).get()
        #    avatar = db_storage.child('Avatar/{}'.format(tutorial_avatar.to_dict()['lessonAvatar'])).get_url("")

        context = {'tutorial_lessons': tutorial_sidebar, 'about_tutorial':about_tutorial,'author_avatar':author_avatar,'zorluk':lst}



        return render(request, 'TutorialLesson.html',context)
    else:
        return redirect('girisSayfasi')


def gotoLesson(request,unitsNames):
    if auth.current_user is not None:

        tutorial_read_data = db.collection(u'tutorial_data_browser').document(u'{}'.format(ders_ismi)).collection(
            u'tutorial_lessons4').document(u'{}'.format(unitsNames))

        tutorial_read_data.update({u'userVisits': firestore.ArrayUnion([u'{}'.format(auth.current_user['localId'])])})


        tutorial_data = db.collection(u'tutorial_data_browser').document(u'{}'.format(ders_ismi)).collection(
            u'tutorial_lessons4').document(u'{}'.format(unitsNames)).get()

        user = db.collection('userData').document(u'{}'.format(auth.current_user['localId'])).get()

        if request.method == 'POST':
            yorum = request.POST['yorum']
            try:
                data = {
                    u'Yorum':yorum,
                    u'Tarih':datetime.datetime.now(),
                    u'Yorum_yapan':user.to_dict()['userFullname'],
                    u'Yorumid':auth.current_user['localId']
                }

                to_comment = db.collection(u'tutorial_data_browser').document(u'{}'.format(ders_ismi))
                comment = to_comment.collection(u'tutorial_lessons4').document(u'{}'.format(unitsNames))
                send_comment = comment.collection(u'Yorumlar').document()
                send_comment.set(data)

            except Exception as err:
                print(err)

        yorum_liste = []
        yorum_avats = []
        to_comments = db.collection(u'tutorial_data_browser').document(u'{}'.format(ders_ismi))
        comments = to_comments.collection(u'tutorial_lessons4').document(u'{}'.format(unitsNames))
        take_comment = comments.collection(u'Yorumlar').get()

        for item in take_comment:
            avatar = db_storage.child('Avatar/{}'.format(item.to_dict()['Yorumid'])).get_url("") # avatarı yansıtamadım..
            yorum_avats.append(avatar)
            yorum_liste.append(item.to_dict())


        return render(request, 'TutorialDetail.html',{'tutorial_data': tutorial_data,'yorumlar':yorum_liste, 'avatars':yorum_avats})

    else:
        return redirect('girisSayfasi')


def books(request):
    if auth.current_user is not None:
        books_data = db.collection('DocumentData').limit(30).stream()

        return render(request, 'Kitaplar.html', {'booksData': books_data})
    else:
        return redirect('girisSayfasi')

def coupons(request):
    if auth.current_user is not None:
        coupons_data = db.collection("BountyData").limit(15).stream()
        return render(request, 'Kupon.html', {"coupon_data":coupons_data})
    else:
        return redirect('girisSayfasi')



def custom_page_not_found_view(request, exception):
    return render(request, "404.html", {})

def custom_error_view(request, exception=None):
    return render(request, "500.html", {})
