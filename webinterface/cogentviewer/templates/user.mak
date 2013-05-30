<%inherit file="base.mak"/>

<%block name="styles">

##<link rel="stylesheet" href="${request.static_url('cogentviewer:jslibs/dojo/dojox/grid/resources/Grid.css')}"/>
##<link rel="stylesheet" href="${request.static_url('cogentviewer:jslibs/dojo/dojox/grid/resources/claroGrid.css')}"/>

</%block>


<%block name="pagecontent">
<h1>Add / Edit User</h1>


<form method="POST" action="" accept-charset="UTF-8" class="form-horizontal">
  <div class="control-group">
    <label class="control-label" for="username">Username</label>
    <div class="controls">
      <div class="input-prepend">
	<span class="add-on"><i class="icon-user"></i></span>
	%if userName:
	    <input class="span12" placeholder="Username" name="username" required="true" value="${userName}" disabled>
	%else:
	    <input class="span12" placeholder="Username" name="username" required="true">
	%endif
      </div>
    </div>
  </div>
    
  <div class="control-group">
    <label class="control-label" for="email">Email</label>
    <div class="controls">
      <div class="input-prepend">
	<span class="add-on"><i class="icon-envelope"></i></span>
	%if userMail:
  	    <input class="span12" placeholder="Email" type="email" name="email" required="true" value="${userMail}"> 
	%else:
	    <input class="span12" placeholder="Email" type="email" name="email" required="true"> 
	%endif
      </div>
    </div>
  </div>

  <div class="control-group">
    <label class="control-label" for="password">Password</label>
    <div class="controls">
      <div class="input-prepend">
	<span class="add-on"><i class="icon-key"></i></span>
	<input class="span12" placeholder="Password" type="password" name="password" required="true"> 
      </div>
    </div>
  </div>
  <button class="btn-info btn" type="submit" name="submit">Login</button>      
</form>    


</%block>
