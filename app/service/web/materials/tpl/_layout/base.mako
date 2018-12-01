<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN""http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <link rel="stylesheet" type="text/css" href="/static/css/bootstrap.min.css">
    <link rel="stylesheet" type="text/css" href="/static/css/bootstrap-table.css">
    <link rel="stylesheet" type="text/css" href="/static/css/font-awesome.min.css">
    <%block name="header"/>
</head>
<body>
    <div class="site-header" role="banner">
        <div class="header fixed">
            <%block></%block>
        <div class="clear"></div>
    </div>
    <div class="container">
        <div class="row">
            <div class="main-page">
            <%block name="content"/>
            </div> <!-- .main-page -->
        </div> <!-- .row -->
        <footer class="row">
            <div class="col-xs-12 col-sm-12 col-md-12 col-lg-12 footer">
                <p class="copyright">Copyright © 2018 datochan</p>
            </div>
        </footer>  <!-- .row -->
    </div> <!-- .container -->

    <!-- JavaScript -->
    <script src="/static/js/jquery.1.11.3.min.js"></script>
    <script src="/static/js/bootstrap.min.js"></script>
    <script src="/static/js/bootstrap-table.js"></script>
    <script src="/static/js/bootstrap-table-sticky-header.js"></script>
    <script src="/static/js/echarts.min.js"></script>
    <%block name="footer"/>
</body>
</html>