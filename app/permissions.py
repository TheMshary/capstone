from rest_framework import permissions

# class IsAuthenticatedOrCreate(permissions.IsAuthenticated):
# 	def has_permission(self, request, view):
# 		if request.method == 'POST':
# 			return True
# 		return super(IsAuthenticatedOrCreate, self).has_permission(request, view)



from rest_framework.authentication import SessionAuthentication 

class CsrfExemptSessionAuthentication(SessionAuthentication):

	def enforce_csrf(self, request):
		return  # To not perform the csrf check previously happening