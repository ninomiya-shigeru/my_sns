from django import forms
from .models import Message, Group, Friend, Joinfriend, Good, Video
from django.contrib.auth.models import User
from django.db.models import Q

# Messageのフォーム（未使用）
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['owner', 'group', 'content']


# Groupのフォーム（未使用）
class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['owner', 'title']


# Friendのフォーム（未使用）
class JoinFriendForm(forms.ModelForm):
    class Meta:
        model = Joinfriend
        fields = ['user', 'group']


# Goodのフォーム（未使用）
class GoodForm(forms.ModelForm):
    class Meta:
        model = Good
        fields = ['owner', 'message']


# Groupのチェックボックスフォーム
class GroupCheckForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(GroupCheckForm, self).__init__(*args, **kwargs)
        wlist = set_group(user)
        #wlist = [('public','public'),('同窓会','同窓会')]
        self.fields['groups'] = forms.MultipleChoiceField(
            choices=wlist,widget=forms.CheckboxSelectMultiple())


# Groupの選択メニューフォーム
class GroupSelectForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(GroupSelectForm, self).__init__(*args, **kwargs)
        self.fields['groups'] = forms.ChoiceField(
            choices=[('-', '-')] + [set_group(user)],
            widget=forms.Select(attrs={'class': 'form-control'}),
        )
        print ('Form❷ get_group=',get_group(user))


class GroupSelect2Form(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(GroupSelect2Form, self).__init__(*args, **kwargs)
        self.fields['groups'] = forms.ChoiceField(
            choices=[('-', '-')] + [(item.title, item.title) for item in Group.objects.filter(owner=user)],
            widget=forms.Select(attrs={'class': 'form-control'})
        )

# Friendのチェックボックスフォーム
class FriendForm(forms.Form):
    def __init__(self, user, friends=[], vals=[], *args, **kwargs):
        super(FriendsForm, self).__init__(*args, **kwargs)
        flist=[(item.user, item.user) for item in friends]
        self.fields['friends'] = forms.MultipleChoiceField(
            choices=flist,
            widget=forms.CheckboxSelectMultiple(),
            initial=vals
        )


#Group作成フォーム
class CreateGroupForm(forms.Form):
    group_name = forms.CharField(max_length=20, \
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))


# 投稿フォーム

class PostForm(forms.Form):
    content = forms.CharField(max_length=2000,
             widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 10}))
    photo1 = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        label='画像1'
    )

    photo2 = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        label='画像2'
    )
    # video_title = forms.CharField(max_length = 125)
    video_file = forms.FileField(required=False)

    def __init__(self, user, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        public = User.objects.filter(username='public').first()
        self.fields['groups'] = forms.ChoiceField(
            choices=set_group(user),
            widget=forms.Select(attrs={'class': 'form-control'}),
        )

class PostForm2(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["content", "group","photo1", "photo2"]
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'photo1': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'photo2': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }


# publicなUserとGroupを取得する
def get_public():
    public_user = User.objects.filter(username='public').first()
    public_group = Group.objects.filter \
        (owner=public_user).first()
    return (public_user, public_group)


# userの属するグループを取得する
def set_group(user):
    sus = Friend.objects.filter(Q(user=user)| Q(owner=user))
    gps = []
    for item in sus:
        gps.append(item.group)
    gps = set(gps)
    w_gps = [('public', 'public')]
    for item in gps:
        w_gps.append((item,item))
    return w_gps


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'video_file']
