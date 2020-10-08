<%inherit file="/_layout/base.mako" />

<%block name="header">
    <link rel="stylesheet" type="text/css" href="/static/css/index.css">
    <title>指数估值信息列表 —— DTGear</title>
</%block>

<%block name="content">
<div class="main-menu">
    <div class="menu-container" style="background-color: #ffffff99;padding: 10px 50px 80px 50px;">
    <h2 class="text-center mgt30 mgb30" style="padding-top: 20px;">
        <a href="#">【${ctx.get("last_date")}】指数估值信息列表</a>
    </h2>
    <table data-toggle="table" data-url="/indexes.json" data-striped="true">
        <thead>
            <tr>
                <th data-field="idx" data-sortable="true" rowspan="2">序号 </th>
                <th data-field="name" rowspan="2">名称</th>
                <th data-field="interest" data-sortable="true" rowspan="2">盈利收益率</th>
                <th data-field="dr" data-sortable="true" rowspan="2">股息率</th>
                <th data-field="roe" data-sortable="true" rowspan="2">ROE</th>
                <th colspan="2" class="text-center">市盈率</th>
                <th colspan="2" class="text-center">市净率</th>
                <th colspan="4" class="text-center">涨跌幅</th>
            </tr>
            <tr>
                <th data-field="PE" data-sortable="true">PE</th>
                <th data-field="PE_RATE" data-sortable="true">百分位 </th>
                <th data-field="PB" data-sortable="true">PB</th>
                <th data-field="PB_RATE" data-sortable="true">百分位</th>
                <th data-field="last_week" data-sortable="true">本周</th>
                <th data-field="last_month" data-sortable="true">本月</th>
                <th data-field="last_quarter" data-sortable="true">本季</th>
                <th data-field="last_year" data-sortable="true">本年</th>
            </tr>
        </thead>
    </table>
    </div>
<div class="clearfix"></div>
</div>

</%block>

<%block name="footer">
<script type="text/javascript">

</script>


</%block>
