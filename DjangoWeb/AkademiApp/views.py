import datetime

from django.shortcuts import render, HttpResponse, redirect, HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.cache import cache
import traceback,random
from AkademiWeb.settings import db, auth, db_storage, DEBUG
from google.cloud import firestore

"""
    Son Kontrol: 20.08.2020 - 19:30 [Cİ]
    
    [Cİ] Tasarımsal geliştirmeler. Bazı backend geliştirmeleri..
    
    - Anasayfa tasarımı geliştirildi
    - Forum yeni konu açma tasarımı ve backend kısmı yapılmalı.

"""


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
                request.session['id'] = logged_user_id

                user_data = db.collection(u'userData').document(request.session['id']).get()
                request.session['avatar'] = db_storage.child('Avatar/{}'.format(user_data.to_dict()['userAvatar'])).get_url("")
                request.session['userFullname'] = user_data.to_dict()['userFullname']
                request.session['userType'] = user_data.to_dict()['userAccountType']
                request.session['userWebsite'] = user_data.to_dict()['userWebsite']
                request.session['userBio'] = user_data.to_dict()['userBio']
                request.session['userEmail'] = user_data.to_dict()['userEmail']
                request.session['userJob'] = user_data.to_dict()['userJob']
                request.session['userUsername'] = user_data.to_dict()['userUsername']
                request.session['userVisitors'] = user_data.to_dict()['userVisitors']



                return redirect('anasayfa')

            except Exception as error:
                if DEBUG:
                    traceback.print_exc()
                return render(request, 'GirisSayfasi.html', {'CVP': 'FALSE'})
        else:
            return render(request, 'GirisSayfasi.html', {})


def anasayfa(request):
    if auth.current_user is not None:
        return render(request, 'Anasayfa.html', {})
    else:
        if DEBUG:
            traceback.print_exc()
        return redirect('girisSayfasi')

def adminPanel(request):

    tutorial_names = db.collection('tutorial_data_browser').get()

    if request.method == 'POST':
        dersad = request.POST['dersadi']
        dersno = request.POST['dersno']
        dersbaslik = request.POST['dersbaslik']
        dersabout = request.POST['about']
        dersicerik = request.POST['dersicerik']
        if 'gönder' in request.POST:
            try:

                data = {
                    "about": dersabout,
                    "name": dersbaslik,
                    "data": dersicerik,
                    "no": int(dersno)}
                to_database = db.collection("tutorial_data_browser").document(dersad).collection("tutorial_lessons4").document(dersbaslik)
                to_database.set(data)

            except Exception as error:
                if DEBUG:
                    traceback.print_exc()
                return render(request, 'DersEkle.html', {'CVP': 'FALSE'})






    return render(request, 'DersEkle.html',{"lessonNames":tutorial_names})

def kullaniciCikis(request):
    if auth.current_user is not None:
        request.session['username'] = None
        request.session['id'] = None
        auth.current_user = None
        return redirect('girisSayfasi')
    else:
        return redirect('girisSayfasi')



def forum(request):
    if auth.current_user is not None:

        forum_topics = db.collection(u'Forum').order_by(u'date', direction=firestore.Query.DESCENDING).limit(15).get()
        user_ids = []
        for item in forum_topics:
            user_ids.append(item.to_dict()['user'])

        forum_avatars = []
        while user_ids:
            commentor_profile = db.collection(u'userData').document(u'{}'.format(user_ids[0])).get()
            commenter_avatar = db_storage.child('Avatar/{}'.format(commentor_profile.to_dict()['userAvatar'])).get_url("")
            forum_avatars.append(commenter_avatar)
            user_ids.pop(0)

        forum_data = db.collection(u'Forum').order_by(u'date', direction=firestore.Query.DESCENDING).limit(15).get()

        return render(request,'Forum.html',{'forum_topic':forum_data,'forum_avatar':forum_avatars})
    else:
        return redirect('girisSayfasi')

def forumIcerik(request,forum_name):
    if auth.current_user is not None:
        commenter = db.collection(u'userData').document(u'{}'.format(auth.current_user['localId'])).get()
        if request.method == 'POST':
            if 'send' in request.POST:
                if 'gonder' == request.POST.get('send'):
                    if 'yorum' in request.POST:
                        yorum = request.POST['yorum']
                        try:
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

            if 'like' in request.POST:
                if 'begen' == request.POST.get('like'):
                    to_like_forum = db.collection(u'Forum').document(u'{}'.format(forum_name))
                    to_like_forum.update({u'upvotes': firestore.ArrayUnion([u'{}'.format(auth.current_user['localId'])])})

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

        user_notes = db.collection(u'browser_user_notes').document(u'{}'.format(auth.current_user['localId']))
        if request.method == 'POST':


            if 'sendnote' in request.POST:
                not_baslik = request.POST['notbaslik']
                not_icerik = request.POST['noticerik']
                try:
                    data = {
                        u"notBaslik": u"{}".format(not_baslik),
                        u"notIcerik":u"{}".format(not_icerik),
                        u"notTarih":u"{}".format(datetime.datetime.now()),
                        u"userUID":u"{}".format(auth.current_user['localId']),
                        u"notDurumu": u"{}".format(False)
                    }

                    user_notes.set(data)

                except:
                    if DEBUG:
                        traceback.print_exc()
                    return render(request,'NotDefteri.html', {})
            if 'nottamam' in request.POST:
                try:
                    data ={
                        u"notDurumu": u"{}".format(True)
                    }
                    user_notes.set(data,merge=True)

                except:
                    if DEBUG:
                        traceback.print_exc()
                    return render(request,'NotDefteri.html', {})

            if 'notsil' in request.POST:
                try:
                    delete_note = db.collection(u'browser_user_notes').document(u'{}'.format(auth.current_user['localId']))
                    delete_note.delete()

                except:
                    if DEBUG:
                        traceback.print_exc()
                    return render(request,'NotDefteri.html', {})


        user_note_data = db.collection(u'browser_user_notes').document(u'{}'.format(auth.current_user['localId'])).get()
        return render(request, 'NotDefteri.html', {'user':user_note_data})
    else:
        return redirect('girisSayfasi')

def ayarlar(request):
    if auth.current_user is not None:
        if request.method == 'POST':
            request.session['userFullname'] = request.POST['name']
            request.session['userWebsite'] = request.POST['site']
            request.session['userBio'] = request.POST['bio']
            request.session['userJob'] = request.POST['meslek']

            try:
                  update_data = db.collection(u'userData').document(u'{}'.format(auth.current_user['localId']))
    
                  data = {
                  u'userFullname':request.session['userFullname'],
                  u'userWebsite':request.session['userWebsite'],
                  u'userBio':request.session['userBio'],
                  u'userJob':request.session['userJob']
                  }
    
                  update_data.set(data,merge=True)
            except:
                if DEBUG:
                    traceback.print_exc()
                return render(request, 'Ayarlar.html')

            return render(request, 'Ayarlar.html')

        return render(request, 'Ayarlar.html')
    else:
        return redirect('girisSayfasi')


def kodYaz(request):
  if auth.current_user is not None:
    return render(request, 'KodYaz.html', {})
  else:
     return redirect('girisSayfasi')

def reset_password(request):
    if request.method == 'POST':
        user_email = request.POST['k_email']
        if 'resetpass' in request.POST:
            try:
                auth.send_password_reset_email(user_email)
                return render(request, 'sifreSifirlama.html', {'onay': 'TRUE'})
            except:
                if DEBUG:
                    traceback.print_exc()
                return render(request, 'sifreSifirlama.html', {'onay': 'FALSE'})

    return render(request, 'sifreSifirlama.html',{})

def profile(request):
    user_data = db.collection(u'userData').document(request.session['id']).get()

    user_stats = db.collection(u'userData').document(request.session['id']).collection(u'statics').document(u'statics').get()

    #Forum konusunun idlerini al.
    user_forum = db.collection("Forum").where("user", "==", "{}".format(request.session['id']))
    results_id = user_forum.stream()
    forum_ids = []
    for item in results_id:
        forum_ids.append(item.id)

    #Kullanıcı avatarını al.
    user_own_data = db.collection(u'userData').document(u'{}'.format(request.session['id'])).get()
    user_account_data = user_own_data.to_dict()
    user_own_avatar = db_storage.child('Avatar/{}'.format(user_account_data['userAvatar'])).get_url("")

    #Forum konusuna yapılmış yorumların uzunluğunu al.
    user_forum_comments = db.collection("Forum").where("user", "==", "{}".format(request.session['id']))
    data = user_forum_comments.stream()
    comments = []
    for item in data:
        comment_data = db.collection(u'Forum').document(u'{}'.format(item.id)).collection(u'comments').get()
        len_data = list(comment_data)
        comments.append(len(len_data))

    #Forum detayını al.
    user_forum = db.collection("Forum").where("user", "==", "{}".format(request.session['id']))
    results = user_forum.stream()

    #Moderatörleri al.
    moderators = db.collection("userData").where("userAccountType", "==", "Moderatör")
    moderator_data = moderators.stream()

    moderators_avatars = []
    for item in moderator_data:
        take_datas = db.collection(u'userData').document('{}'.format(item.id)).get()
        avatar = db_storage.child('Avatar/{}'.format(take_datas.to_dict()['userAvatar'])).get_url("")
        moderators_avatars.append(avatar)

    mods = db.collection("userData").where("userAccountType", "==", "Moderatör")
    mods_data = mods.stream()


    #Kullanıcı eğitimlerini al.
    to_lesson_avatars = db.collection(u'userData').document('{}'.format(request.session['id'])).collection(u'tutorials').get()
    ders_avatars = []
    for item in to_lesson_avatars:
        tutorial_avatar = db.collection(u'v2TutorialData').document(u'{}'.format(item.id)).get()
        try:ders_avatars.append(db_storage.child('tutorialFiles/{}'.format(tutorial_avatar.to_dict()['lessonAvatar'])).get_url(""))
        except:pass

    user_tutorial = db.collection(u'userData').document('{}'.format(request.session['id'])).collection(u'tutorials').get()

    # Forum Konularını al.
    forum_topics = db.collection(u'Forum').order_by(u'date',direction=firestore.Query.DESCENDING).limit(5).get()

    #Forum konularının avatarlarını al.
    forum_to_avatar = db.collection(u'Forum').order_by('date').limit(5).get()
    user_forum_avatars = []
    for item in forum_to_avatar:
        to_avatars = db.collection(u'userData').document(u'{}'.format(item.to_dict()['user'])).get()
        user_forum_avatars.append(db_storage.child('Avatar/{}'.format(to_avatars.to_dict()['userAvatar'])).get_url(""))

    context = {'user':user_data.to_dict(),'avatar':user_own_avatar, 'user_stat':user_stats,'forums':results, 'comments':comments, 'forum_detay':forum_ids, 'moderators':mods_data, 'modavatars':moderators_avatars,
               'tutorials':user_tutorial, 'tutorial_avats':ders_avatars,'forum_topics':forum_topics,'forum_user':user_forum_avatars}

    return render(request, 'Profil.html', context)

def other_profiles(request,otherUser):
    if auth.current_user is not None:
        if request.method == 'POST':
            if 'takipet' in request.POST:
                # OtherUser haricinde kendi bilgilerimizi de update etmeliyiz.
                user_to_follow = db.collection(u'userData').document(u'{}'.format(otherUser))

                user_to_follow.update(
                    {u'userFollowers': firestore.ArrayUnion([u'{}'.format(auth.current_user['localId'])])})

            if 'unfollow' in request.POST:
                user_to_unfollow = db.collection(u'userData').document(u'{}'.format(otherUser))
                user_to_unfollow.update(
                    {u'userFollowers': firestore.ArrayRemove([u'{}'.format(auth.current_user['localId'])])})

        user_data = db.collection(u'userData').document(otherUser).get()
        request.session['id2'] = otherUser
        request.session['avatar2'] = db_storage.child('Avatar/{}'.format(user_data.to_dict()['userAvatar'])).get_url("")
        request.session['userFullname2'] = user_data.to_dict()['userFullname']
        request.session['userType2'] = user_data.to_dict()['userAccountType']
        request.session['userWebsite2'] = user_data.to_dict()['userWebsite']
        request.session['userRegistrationDate2'] = str(user_data.to_dict()['userRegistrationDate'])[:10]
        request.session['userBio2'] = user_data.to_dict()['userBio']
        request.session['userEmail2'] = user_data.to_dict()['userEmail']
        request.session['userJob2'] = user_data.to_dict()['userJob']
        request.session['userUsername2'] = user_data.to_dict()['userUsername']
        request.session['userVisitors2'] = user_data.to_dict()['userVisitors']
        request.session['userPoint2'] = user_data.to_dict()['userPoint']
        request.session['userFollowing2'] = user_data.to_dict()['userFollowing']
        request.session['userFollowers2'] = user_data.to_dict()['userFollowers']

        user_stats = db.collection(u'userData').document(U'{}'.format(otherUser)).collection(u'statics').document(
            u'statics').get()

        # Forum konusunun idlerini al.
        user_forum = db.collection("Forum").where("user", "==", "{}".format(otherUser))
        results_id = user_forum.stream()
        forum_ids = []
        for item in results_id:
            forum_ids.append(item.id)

        # Forum konusuna yapılmış yorumların uzunluğunu al.
        user_forum_comments = db.collection("Forum").where("user", "==", "{}".format(otherUser))
        data = user_forum_comments.stream()
        comments = []
        for item in data:
            comment_data = db.collection(u'Forum').document(u'{}'.format(item.id)).collection(u'comments').get()
            len_data = list(comment_data)
            comments.append(len(len_data))

        # Forum detayını al.
        user_forum = db.collection("Forum").where("user", "==", "{}".format(otherUser))
        results = user_forum.stream()

        # Moderatörleri al.
        moderators = db.collection("userData").where("userAccountType", "==", "Moderatör")
        moderator_data = moderators.limit(5).stream()

        moderators_avatars = []
        for item in moderator_data:
            take_datas = db.collection(u'userData').document('{}'.format(item.id)).get()
            avatar = db_storage.child('Avatar/{}'.format(take_datas.to_dict()['userAvatar'])).get_url("")
            moderators_avatars.append(avatar)

        mods = db.collection("userData").where("userAccountType", "==", "Moderatör")
        mods_data = mods.limit(5).stream()

        # Kullanıcı eğitimlerini al.
        to_lesson_avatars = db.collection(u'userData').document('{}'.format(otherUser)).collection(u'tutorials').get()
        ders_avatars = []
        for item in to_lesson_avatars:
            tutorial_avatar = db.collection(u'v2TutorialData').document(u'{}'.format(item.id)).get()
            try:ders_avatars.append(db_storage.child('tutorialFiles/{}'.format(tutorial_avatar.to_dict()['lessonAvatar'])).get_url(""))
            except: pass

        user_tutorial = db.collection(u'userData').document('{}'.format(otherUser)).collection(u'tutorials').get()

        # Forum Konularını al.
        forum_topics = db.collection(u'Forum').order_by(u'date', direction=firestore.Query.DESCENDING).limit(5).get()

        # Forum konularının avatarlarını al.
        forum_to_avatar = db.collection(u'Forum').order_by('date').limit(5).get()
        user_forum_avatars = []
        for item in forum_to_avatar:
            to_avatars = db.collection(u'userData').document(u'{}'.format(item.to_dict()['user'])).get()
            user_forum_avatars.append(db_storage.child('Avatar/{}'.format(to_avatars.to_dict()['userAvatar'])).get_url(""))

        context = {'user_stat':user_stats, 'forums': results, 'comments': comments, 'forum_detay': forum_ids,
                   'moderators': mods_data, 'modavatars': moderators_avatars,
                   'tutorials': user_tutorial, 'tutorial_avats': ders_avatars, 'forum_topics': forum_topics,
                   'forum_user': user_forum_avatars}

        return render(request, 'OtherProfil.html', context)
    else:
        return redirect('girisSayfasi')



def news(request):
    if auth.current_user is not None:

        news_data = db.collection(u'News').order_by(u'date', direction=firestore.Query.DESCENDING).limit(15).get()

        return render(request, 'Bulten.html', {'newsData': news_data})
    else:
        return redirect('girisSayfasi')


def tutorial_dashboard(request):
    if auth.current_user is not None:
        tutorial_names = db.collection(u'tutorial_data_browser').get()

        return render(request, 'Egitimler.html', {'lesson_names':tutorial_names})

    else:
        return redirect('girisSayfasi')



def tutorial_detail(request,lesson_names):
    if auth.current_user is not None:
        global ders_ismi
        ders_ismi = lesson_names
        tutorial_sidebar = db.collection(u'tutorial_data_browser').document(u'{}'.format(ders_ismi)).collection(u'tutorial_lessons4').order_by(u'no').stream()

        about_tutorial = db.collection(u'tutorial_data_browser').document(u'{}'.format(ders_ismi)).get()

        author_data = db.collection(u'userData').document(u'{}'.format(about_tutorial.to_dict()['Authorid'])).get()

        author_avatar = db_storage.child('Avatar/{}'.format(author_data.to_dict()['userAvatar'])).get_url("")

        zorluk = [1,5,6,7,8,9,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,91,92,93,94,95,96,97,98,99,100]

        if ders_ismi == "BeautifulSoup4":
            tutorial_avatar = db.collection(u'v2TutorialData').document(u'Python').get()
            avatar = db_storage.child('tutorialFiles/{}'.format(tutorial_avatar.to_dict()['lessonAvatar'])).get_url("")

        elif  ders_ismi == 'Nodejs':
            tutorial_avatar = db.collection(u'v2TutorialData').document(u'Javascript').get()
            avatar = db_storage.child('tutorialFiles/{}'.format(tutorial_avatar.to_dict()['lessonAvatar'])).get_url("")

        elif ders_ismi == 'Numpy':
            tutorial_avatar = db.collection(u'v2TutorialData').document(u'Python').get()
            avatar = db_storage.child('tutorialFiles/{}'.format(tutorial_avatar.to_dict()['lessonAvatar'])).get_url("")

        elif ders_ismi == 'MySql':
            tutorial_avatar = db.collection(u'v2TutorialData').document(u'Mysql').get()
            avatar = db_storage.child('tutorialFiles/{}'.format(tutorial_avatar.to_dict()['lessonAvatar'])).get_url("")
        elif ders_ismi == 'MsSql':
            tutorial_avatar = db.collection(u'v2TutorialData').document(u'Mysql').get()
            avatar = db_storage.child('tutorialFiles/{}'.format(tutorial_avatar.to_dict()['lessonAvatar'])).get_url("")
        elif ders_ismi == 'Derleyici Tasarımı':
            tutorial_avatar = db.collection(u'v2TutorialData').document(u'Mysql').get()
            avatar = db_storage.child('tutorialFiles/{}'.format(tutorial_avatar.to_dict()['lessonAvatar'])).get_url("")

        else:
            tutorial_avatar = db.collection(u'v2TutorialData').document(u'{}'.format(ders_ismi)).get()
            avatar = db_storage.child('tutorialFiles/{}'.format(tutorial_avatar.to_dict()['lessonAvatar'])).get_url("")

        context = {'tutorial_lessons': tutorial_sidebar, 'about_tutorial':about_tutorial,'author_avatar':author_avatar,'zorluk':zorluk, 'avatar':avatar}



        return render(request, 'TutorialLesson.html',context)
    else:
        return redirect('girisSayfasi')


def gotoLesson(request,unitsNames):
    if auth.current_user is not None:
        to_comment = db.collection(u'tutorial_data_browser').document(u'{}'.format(ders_ismi))
        comment = to_comment.collection(u'tutorial_lessons4').document(u'{}'.format(unitsNames))
        send_comment = comment.collection(u'Yorumlar').document()
        user = db.collection('userData').document(u'{}'.format(auth.current_user['localId'])).get()
        if request.method == 'POST':
            if 'yorum' in request.POST:
                yorum = request.POST['yorum']
                try:
                    data = {
                        u'Yorum': yorum,
                        u'Tarih': datetime.datetime.now(),
                        u'Yorum_yapan': user.to_dict()['userFullname'],
                        u'Yorumid': auth.current_user['localId'],
                    }

                    send_comment.set(data)

                except Exception as err:
                    print(err)

            if 'like' in request.POST:
                to_like = db.collection(u'tutorial_data_browser').document(u'{}'.format(ders_ismi))
                like = to_like.collection(u'tutorial_lessons4').document(u'{}'.format(unitsNames))
                send_like = like.collection(u'Yorumlar').get()

                all_comments = []
                for item in send_like:
                    all_comments.append(item.id)

                for i in range(0, len(all_comments)):
                    if str(i) == request.POST.get('like'):
                        a = like.collection(u'Yorumlar').document(u'{}'.format(all_comments[i]))
                        a.update({u'begeniler': firestore.ArrayUnion([u'{}'.format(auth.current_user['localId'])])})

            if 'yorumsil' in request.POST:
                to_delete = db.collection(u'tutorial_data_browser').document(u'{}'.format(ders_ismi))
                delete = to_delete.collection(u'tutorial_lessons4').document(u'{}'.format(unitsNames))
                send_delete = delete.collection(u'Yorumlar').get()

                all_comments = []
                for item in send_delete:
                    all_comments.append(item.id)

                for i in range(0, len(all_comments)):
                    if str(i) == request.POST.get('yorumsil'):
                        a = delete.collection(u'Yorumlar').document(u'{}'.format(all_comments[i]))
                        a.delete()


        tutorial_read_data = db.collection(u'tutorial_data_browser').document(u'{}'.format(ders_ismi)).collection(
            u'tutorial_lessons4').document(u'{}'.format(unitsNames))

        tutorial_read_data.update({u'userVisits': firestore.ArrayUnion([u'{}'.format(auth.current_user['localId'])])})

        tutorial_read_count = db.collection(u'userData').document(u'{}'.format(request.session['id'])).collection(u'tutorials').document(u'{}'.format(ders_ismi))
        tutorial_read_count.set({
            u'userTutorialLastLesson': firestore.Increment(1)
        },merge=True)


        tutorial_data = db.collection(u'tutorial_data_browser').document(u'{}'.format(ders_ismi)).collection(
            u'tutorial_lessons4').document(u'{}'.format(unitsNames)).get()

        yorum_liste = []
        yorum_avats = []
        to_comments = db.collection(u'tutorial_data_browser').document(u'{}'.format(ders_ismi))
        comments = to_comments.collection(u'tutorial_lessons4').document(u'{}'.format(unitsNames))
        take_comment = comments.collection(u'Yorumlar').get()


        for item in take_comment:
            userData = db.collection('userData').document(u'{}'.format(item.to_dict()['Yorumid'])).get()
            avatar = db_storage.child('Avatar/{}'.format(userData.to_dict()['userAvatar'])).get_url("")
            yorum_avats.append(avatar)
            yorum_liste.append(item.to_dict())

        tutorial_detay = db.collection(u'tutorial_data_browser').document(u'{}'.format(ders_ismi)).get()


        return render(request, 'TutorialDetail.html',{'tutorial_data': tutorial_data,'yorumlar':yorum_liste, 'avatars':yorum_avats,'tuto_detail':tutorial_detay})

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

def lessonexam(request):

    return render(request,'lessonExam.html')

def certificatePage(request):

    request.session['lessonName'] = ders_ismi
    return render(request,'certificate.html')


def custom_page_not_found_view(request, exception):
    return render(request, "404.html", {})

def custom_error_view(request, exception=None):
    return render(request, "500.html", {})
