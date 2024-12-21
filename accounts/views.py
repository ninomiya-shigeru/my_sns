from django.views import generic
from .forms import LoginForm # 追加
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView  # 追加
from .forms import LoginForm, SignupForm, UserUpdateForm, MyPasswordChangeForm # 追加
from django.shortcuts import redirect, resolve_url # 追加
from django.contrib.auth import get_user_model # 追加
from django.contrib.auth.mixins import UserPassesTestMixin # 追加
from django.urls import reverse_lazy

'''トップページ'''
class TopView(generic.TemplateView):
    template_name = 'accounts/top.html'


class Login(LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'

'''追加'''
class Logout(LogoutView):
    template_name = 'accounts/logout_done.html'

'''自分しかアクセスできないようにするMixin(My Pageのため)'''
class OnlyYouMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        # 今ログインしてるユーザーのpkと、そのマイページのpkが同じなら許可
        user = self.request.user
        return user.pk == self.kwargs['pk']


'''マイページ'''
class My_Page(OnlyYouMixin, generic.DetailView):
    model = get_user_model()
    template_name = 'accounts/my_page.html'
    # モデル名小文字(user)でモデルインスタンスがテンプレートファイルに渡される

'''サインアップ'''
class Signup(generic.CreateView):
    template_name = 'accounts/signup.html'
    form_class =SignupForm

    def form_valid(self, form):
        user = form.save()  # formの情報を保存
        return redirect('accounts:signup_done')

    # データ送信
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["process_name"] = "Sign up"
        return context


'''サインアップ完了'''
class SignupDone(generic.TemplateView):
    template_name = 'accounts/signup_done.html'


'''ユーザー登録情報の更新'''
class UserUpdate(OnlyYouMixin, generic.UpdateView):
    model = get_user_model()
    form_class = UserUpdateForm
    template_name = 'accounts/user_form.html'

    def get_success_url(self):
        return resolve_url('accounts:my_page', pk=self.kwargs['pk'])

    # contextデータ作成
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["process_name"] = "Update"
        return context

'''パスワード変更'''
class PasswordChange(PasswordChangeView):
    form_class = MyPasswordChangeForm
    success_url = reverse_lazy('accounts:password_change_done')
    template_name = 'accounts/user_form.html'

    # contextデータ作成
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["process_name"] = "Change Password"
        return context


'''パスワード変更完了'''
class PasswordChangeDone(PasswordChangeDoneView):
    template_name = 'accounts/password_change_done.html'