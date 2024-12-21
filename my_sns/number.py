from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http import HttpResponse
from django.core.mail import send_mail, EmailMessage

from .models import Message, Friend, Joinfriend, Group, Good, Comment
from .forms import GroupCheckForm, GroupSelectForm, GroupSelect2Form,\
    FriendForm, JoinFriendForm, CreateGroupForm, PostForm, GroupForm
import datetime

def health_check(request):
    # 必要に応じて、追加のロジックをここに記述します
    # メール送付
    subject = "private-SNSグループ加入申請"
    honbun =  'XXさんからに加入申請が>きました。' \
                  + 'グループページから申請を許可するか、却下してください！'
    from_mail = "sh-ninomiya@c02.itscom.net"
    to_mail_list = [
        'ninomiya@netssc.co.jp'
    ]
    email = EmailMessage(subject, honbun, from_mail, to_mail_list)
    email.send()
    return HttpResponse("Email send")   # Viewに追加


# ユーザー認証関数
def top(request):
    a =  1
    return render(request, 'sns/top.html')


# indexのビュー関数
@login_required(login_url='/accounts/login/')
def index(request, page=1):
    # publicのuserを取得
    (public_user, public_group) = get_public()

    # POST送信時の処理
    if request.method == 'POST':

        # Groupsのチェックを更新した時の処理
        # フォームの用意
        checkform = GroupCheckForm(request.user, request.POST)
        # チェックされたGroup名をリストにまとめる
        glist = []
        for item in request.POST.getlist('groups'):
            glist.append(item)
         # Messageの取得
        messages = get_your_group_message(request.user, glist, page)
        print ('Index❶ request.user=',request.user,'glist=',glist,len(messages))
    # GETアクセス時の処理
    else:
        # フォームの用意
        checkform = GroupCheckForm(request.user)
        # request.userの属するGroupのリストを取得
        glist=get_group(request.user)
        # メッセージの取得
        messages = get_your_group_message(request.user, glist, page)
        print ('Index❷ request.user=', request.user, 'glist=',glist,len(messages))
    #  共通処理
    comments = Comment.objects.all
    params = {
        'login_user': request.user,
        'contents': messages,
        'check_form': checkform,
        'comments': comments,
    }
    return render(request, 'sns/index.html', params)


@login_required
def delete(request, num):
    print('delete❶', num)
    if (request.method == 'POST'):
        # msgid = request.GET['msg_id']
        obj = Message.objects.get(id=num)
        obj.delete()
        print('delete')
        messages.success(request, 'メッセージを削除しました！')
        return redirect(to='index')
    else:
        obj = Message.objects.get(id=num)
        if str(obj.owner) != str(request.user):  # ユーザーオブジェクトを文字列に変換
            print('delete❷=', num, str(obj.owner), str(request.user))
            messages.success(request, '自分以外の投稿は削除できません！')
            return redirect(to='index')
        else:
            # フォームの各フィールドに値を手動でセット
            form = PostForm(request.user)
            form.fields['content'].initial = obj.content
            form.fields['groups'].initial = obj.group
            params = {
                # 'msgid': msgid,
                'message': obj,
                'form': form
            }
            return render(request, 'sns/delete.html', params)

@login_required
def edit(request, num):
    obj = Message.objects.get(id=num)
    if request.method == 'POST':
        # 送信内容の取得
        gr_name = request.POST['groups']
        content = request.POST['content']
        # Groupの取得
        group = Group.objects.filter(title=gr_name).first()
        print('edit❶ _gr_name;',gr_name,'group;',group,content)
        if group == None:
            (pub_user, group) = get_public()
        # Messageを作成し設定して保存
        obj.owner = request.user
        obj.group = group     # ***** 24/2/7 *****
        obj.content = content
        obj.save()
        # メッセージを設定
        messages.success(request, 'メッセージを編集しました！')
        return redirect(to='index')
    # GETリクエスト
    else:
        if str(obj.owner) != str(request.user):
            print('edit❷=', obj.owner, request.user)
            messages.success(request, '自分以外の投稿は編集できません！')
            return redirect(to='index')
        else:
            # フォームの各フィールドに値を手動でセット
            form = PostForm(request.user)
            form.fields['content'].initial = obj.content
            form.fields['groups'].initial = obj.group
            params = {
                'message': obj,
                'form': form
            }
            return render(request, 'sns/edit.html', params)


@login_required
def comment(request):
    if request.method == 'POST':
        content = request.POST['cmt']
        print("comment❶")
        cmnt = Comment()
        cmnt.text = content
        cmnt.commented_to = Message.objects.get(id=request.GET['msg_id'])
        cmnt.commented_by = request.user
        cmnt.save()
        # コメントを投稿しました
        # messages.success(request,'新しいコメントを投稿しました！')
        return redirect(to='index')
    # GETリクエスト
    else:
        print('cmment❷')
        msgid = request.GET['msg_id']
        owner = request.GET['owner']
        the_message = Message.objects.get(id=msgid)
        comments = Comment.objects.filter(commented_to=the_message)
        comments = Comment.objects.filter(commented_to=msgid)

        # form = CommentForm(request)

    params = {
        'msgid': msgid,
        'message': the_message,
        'comments': comments,
    }
    return render(request, 'sns/comment.html', params)


# メッセージのポスト処理
@login_required(login_url='/accounts/login/')
def post(request):
    # POST送信の処理
    if request.method == 'POST':
        # 送信内容の取得
#"""
        #gr_name = request.POST['groups']
        #content = request.POST['content']
        #photo1 = request.FILES.get('photo1')
        #photo2 = request.FILES.get('photo2')
        # Groupの取得
        #group = Group.objects.filter(title=gr_name).first()
        #print ('Post❶ _gr_name;',gr_name,'group;',group,content)
        #if group == None:
        #    (pub_user, group) = get_public()
        # Messageを作成し設定して保存
        #msg = Message()
        #msg.owner = request.user
        #msg.group = group     # ***** 24/2/7 *****
        #msg.content = content
        #msg.photo1 = photo1
        #msg.photo2 = photo2
        #msg.save()

        form = PostForm(request.POST, request.FILES)
        if form.is_valit():
            message_instance = form.save(commit=False)
            group = Group.objects.filter(title=gr_name).first()
            print ('Post❶ _gr_name;',gr_name,'group;',group,content)
            if group == None:
                (pub_user, group) = get_public()
            post_instance.save()


        # メッセージを設定
        messages.success(request, '新しいメッセージを投稿しました！')
        # メール送付
        subject = "Private-SNS"
        honbun =  'さんから新しいメッセージが投稿されました'
        from_mail = "sh-ninomiya@c02.itscom.net"
        to_mail_list = [
               'sh-ninomiya@c02.itscom.net'
        ]
        email = EmailMessage(subject, honbun, from_mail, to_mail_list)
        email.send()

        return redirect(to='index')

    # GETアクセス時の処理
    else:
        form = PostForm(request.user)

    # 共通処理
    params = {
        'login_user': request.user,
        'form': form,
    }
    return render(request, 'sns/post.html', params)


@login_required(login_url='/admin/login/')
def groups(request):
    # 自分が登録したFriendを取得
    friends = Friend.objects.filter(owner=request.user)
    print ('Group❶ friends=',friends)
    # POST送信時の処理
    if request.method == 'POST':

        # Groupsメニュー選択肢の処理
        if request.POST['mode'] == '__groups_form__':
            # 選択したGroup名を取得
            sel_group = request.POST['groups']
            # Groupを取得
            gp = Group.objects.filter(title=sel_group).first()
            # Groupに含まれるFriendを取得
            fds = Friend.objects.filter(group=gp)     # *******************
            print ('Group❷ sel_group=',sel_group,'GP=',gp,'fds=',fds)
            # FriendのUserをリストにまとめる
            vlist = []
            for item in fds:
                vlist.append(item.user.username)
            print ('Group❸ fds=',fds,' vlist=',vlist)
            # フォームの用意
            groupsform = GroupSelect2Form(request.user, request.POST)
            friendsform = FriendsForm(request.user, \
                                      friends=friends, vals=vlist)

        # Friendsのチェック更新時の処理
        if request.POST['mode'] == '__friends_form__':
            # 選択したGroupの取得
            sel_group = request.POST['group']
            group_obj = Group.objects.filter(title=sel_group).first()
            # チェックしたFriendsを取得
            sel_fds = request.POST.getlist('friends')
            # FriendsのUserを取得
            sel_users = User.objects.filter(username__in=sel_fds)
            # Userのリストに含まれるユーザーが登録したFriendを取得
            fds = Friend.objects.filter(owner=request.user) \
                .filter(user__in=sel_users)
            # すべてのFriendにGroupを設定し保存する
            vlist = []
            for item in fds:
                item.group = group_obj
                item.save()
                vlist.append(item.user.username)
            print('Group❻ sel_group=', sel_group, 'fds=', fds)
            # メッセージを設定
            messages.success(request, ' チェックされたFriendを' + \
                             sel_group + 'に登録しました。')
            # フォームの用意
            groupsform = GroupSelect2Form(request.user, \
                                         {'groups': sel_group})
            friendsform = FriendsForm(request.user, \
                                      friends=friends, vals=vlist)

    # GETアクセス時の処理
    else:
        # フォームの用意
        groupsform = Group.objects.all()
        joinfriendform = Joinfriend.objects.all()
        sel_group = '-'

    # 共通処理
    createform = CreateGroupForm()
    params = {
        'login_user': request.user,
        'groups_form': groupsform,
        'friends_form': joinfriendform,
        'create_form': createform,
        'group': sel_group,
    }
    print ('Group❼request.user=',request.user,'groupsform=',groupsform,joinfriendform,createform,sel_group)
    return render(request, 'sns/groups.html', params)


# Friendの加入申請処理
@login_required(login_url='/admin/login/')
def add(request):
    # 追加するUserを取得
    add_user = request.user
    add_name = request.GET['owner']
    add_owner = User.objects.filter(username=add_name).first()
    add_group = request.GET['group'] #django.utils.datastructures.MultiValueDictKeyError: 'group'
    add_group = Group.objects.filter(title=add_group).first()
    print ('add❶ add_user=',add_user,'add_group=',add_group)
    # Userが本人だった場合の処理
    if add_user == add_owner:
        messages.info(request, "自分自身をグループに追加することはできません。")
        return redirect(to='/groups')
    # add_userのFriendの数を調べる
    frd_num = Friend.objects.filter(owner=add_user).filter(group=add_group).count()
    #filter(group=add.group)
    print('add❷ frd_num=', frd_num, 'add_name=', add_name)
    # ゼロより大きければ既に登録済み
    if frd_num > 0:
        messages.info(request, add_user.username + 'さんは既に追加されています。')
        return redirect(to='/groups')
    # 加入申請済みか調べる
    joi_num=Joinfriend.objects.filter(user=add_user).filter(group=add_group).count()
    if joi_num > 0:
        messages.info(request, add_user.username + 'さんは既に申請されています。')
        return redirect(to='/groups')

    # メール送付
    # subject = "private-SNSグループ加入申請"
    # honbun = frd.user.username + 'さんから' + frd.group.title + 'に加入申請がきました。' \
    #               + 'グループページから申請を許可するか、却下してください！'
    # from_mail = "private_sns@sh-ninomiya.com"
    # to_mail_list = [
    # add_owner.email
    # ]
    # send_mail(subject, honbun, from_mail, to_mail_list, fail_silently=False)

# ここからFriendの登録処理
    frd = Joinfriend(user=add_user)
    frd.user = request.user
    frd.group = Group.objects.filter(title=add_group).first()
    frd.hope_date = datetime.datetime.now()
    frd.join_date = '00/00/00'
    frd.save()
    print ('add❸ add_user=',frd.user,'group=',frd.group)
    # メッセージを設定
    messages.success(request, add_user.username + 'さんを追加しました!')

    return redirect(to='/groups')


# Friendの加入承認処理
@login_required(login_url='/admin/login/')
def join(request):
    # 追加するUserを取得
    print ('Join❶=',request.GET['menber'],request.GET['group'])
    obj_menber = User.objects.filter(username=request.GET['menber']).first()
    obj_group = Group.objects.filter(title=request.GET['group']).first    # *** Friend has no group **************

    #グループのオーナー取り込み
    group_instance = Group.objects.get(title=request.GET['group'])
    owner_value = group_instance.owner
    print ('join❷ obj_menber=',obj_menber,'group_instance=',group_instance,'owner_value=',owner_value)

    # Userが本人だった場合の処理
    if owner_value != request.user:
        messages.info(request, "あなたには加入承認することはできません。")
        return redirect(to='/groups')

    # ここからFriendの登録処理
    frd = Friend()
    frd.owner =owner_value
    frd.user =obj_menber
    frd.group = group_instance
    frd.save()
    print('join❹ frd.owner=', frd.owner, 'frd.user=', frd.user, 'frd.group=', frd.group)

    jfd=Joinfriend.objects.get(group=group_instance,user=obj_menber)
    # jfd.join_date = datetime.datetime.now()
    # print (jfd,jfd.join_date)
    # jfd.save()
    jfd.delete()
    #messages.success(request, group_instance + ' に' + obj_menber + ' を追加しました！
    return redirect(to='/groups')

# Friendの加入却下処理
@login_required(login_url='/admin/login/')
def rjct(request):
    # 却下するUserを取得
    rjc_menber = User.objects.filter(username=request.GET['menber']).first()
    rjc_group = Group.objects.filter(title=request.GET['group']).first    # *** Friend has no group **************

    #グループのオーナー取り込み
    group_instance = Group.objects.get(title=request.GET['group'])
    owner_value = group_instance.owner

    # Userが本人だった場合の処理
    if owner_value != request.user:
        messages.info(request, "あなたには加入却下することはできません。")
        return redirect(to='/groups')
    #申請の却下処理
    jfd=Joinfriend.objects.get(group=group_instance,user=rjc_menber)
    jfd.delete()
    messages.success(request, group_instance + ' に' + rjc_menber + 'さんの申請を却下しました！')
    return redirect(to='/groups')

# グループの作成処理
@login_required(login_url='/admin/login/')
def creategroup(request):
    # Groupを作り、Userとtitleを設定して保存する
    gp = Group()
    gp.owner = request.user
    gp.title = request.user.username + 'の' + request.POST['group_name']
    gp.save()
    messages.info(request, '新しいグループを作成しました。')
    return redirect(to='/groups')




# 投稿をシェアする
@login_required(login_url='/admin/login/')
def share(request, share_id):
    # シェアするMessageの取得
    share = Message.objects.get(id=share_id)
    print(share)
    # POST送信時の処理
    if request.method == 'POST':
        # 送信内容を取得
        gr_name = request.POST['groups']
        content = request.POST['content']
        # Groupの取得
        group = Group.objects.filter(owner=request.user) \
            .filter(title=gr_name).first()
        if group == None:
            (pub_user, group) = get_public()
        # メッセージを作成し、設定をして保存
        msg = Message()
        msg.owner = request.user
        msg.group = group
        msg.content = content
        msg.share_id = share.id
        msg.save()
        share_msg = msg.get_share()
        share_msg.share_count += 1
        share_msg.save()
        # メッセージを設定
        messages.success(request, 'メッセージをシェアしました！')
        return redirect(to='/index')

    # 共通処理
    form = PostForm(request.user)
    params = {
        'login_user': request.user,
        'form': form,
        'share': share,
    }
    return render(request, 'sns/share.html', params)


# goodボタンの処理
@login_required(login_url='/admin/login/')
def good(request, good_id):
    # goodするMessageを取得
    good_msg = Message.objects.get(id=good_id)
    # 自分がメッセージにGoodした数を調べる
    is_good = Good.objects.filter(owner=request.user) \
        .filter(message=good_msg).count()
    # ゼロより大きければ既にgood済み
    if is_good > 0:
        messages.success(request, '既にメッセージにはGoodしています。')
        return redirect(to='/index')

    # Messageのgood_countを１増やす
    good_msg.good_count += 1
    good_msg.save()
    # Goodを作成し、設定して保存
    good = Good()
    good.owner = request.user
    good.message = good_msg
    good.save()
    # メッセージを設定
    messages.success(request, 'メッセージにGoodしました！')
    return redirect(to='/index')


# ===================これ以降は普通の関数==================

# 指定されたグループおよび検索文字によるMessageの取得
def get_your_group_message(user, glist, page):
    page_num = 10  # ページあたりの表示数
    (public_user, public_group) = get_public()           # publicの取得
    groups = Group.objects.filter(title__in=glist)       # チェックされたGroupの取得
    print ('GetYMsg❶ groups=', groups, ' user=', user, ' glist=', glist)
    me_friends = Friend.objects.filter(group__in=groups)  # Groupに含まれるFriendの取得
    # FriendのUserをリストにまとめる
    me_users = []
    for f in me_friends:
        me_users.append(f.user)
    # groupがgroupsに含まれるか、me_groupsに含まれるMessageの取得
    messages = Message.objects.filter(group__in=groups)
    # ページネーションで指定ページを取得
    page_item = Paginator(messages, page_num)
    print ('GetYMmsg❷ ', len(messages))
    return page_item.get_page(page)


# publicなUserとGroupを取得する
def get_public():
    public_user = User.objects.filter(username='public').first()
    public_group = Group.objects.filter(owner=public_user).first()
    return (public_user, public_group)

# userの属するグループを取得する
def get_group(user):
    sus = Friend.objects.filter(Q(user=user) | Q(owner=user)) # ***** 24/2/7 *****
    gps = []
    for item in sus:
        gps.append(item.group)
    (public_user, public_group) = get_public()
    glist = [public_group]
    for item in gps:
        glist.append((item.title))
    glist = set(glist)           # 重複削除
    print('Get_group❶ gps=', gps, ' glist;', glist)  # ***** 24/2/5 *****
    return glist
