from rest_framework import permissions


class IsQiniuCallback(permissions.BasePermission):

    def has_permission(self, request, view):
        from . import QINIU_CB_URL_PHOTO_UPLOAD
        original_authorization = get_authorization_header(request)
        callback_url = QINIU_CB_URL_PHOTO_UPLOAD
        body = request.body
        return qiniu_auth.verify_callback(original_authorization, callback_url, body)