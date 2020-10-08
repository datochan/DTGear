<%inherit file="/_layout/base.mako" />

<%block name="header">
    <link rel="stylesheet" type="text/css" href="/static/css/index.css">
    <title>首页 —— DTGear</title>
</%block>

<%block name="content">
<div class="main-menu">
    <div class="menu-container">
        <div class="col-xs-6 col-md-12">
            <div id="total_top" class="main-menu-link thumbnail hq-k-line"> </div>
        </div>
    </div>

    <div class="menu-container">
        <div class="col-xs-6 col-md-3">
            <a href="/indexes" class="main-menu-link thumbnail filter">
                <i class="fa fa-bar-chart-o fa-4x main-menu-link-icon"></i>
                指数估值
            </a>
        </div>

        <div class="col-xs-6 col-md-3">
            <a href="javascript:alert('功能暂未实现!');" class="main-menu-link thumbnail status-error">
                <i class="fa fa-filter fa-4x main-menu-link-icon"></i>
                个股信息
            </a>
        </div>
        <div class="col-xs-6 col-md-3">
            <a href="javascript:alert('功能暂未实现!');" class="main-menu-link thumbnail longhu">
                <i class="fa fa-cubes fa-4x main-menu-link-icon"></i>
                财报研究
            </a>
        </div>
        <div class="col-xs-6 col-md-3">
            <a href="javascript:alert('功能暂未实现!');" class="main-menu-link thumbnail zhuangjia">
                <i class="fa fa-users fa-4x main-menu-link-icon"></i>
                回测工具
            </a>
        </div>
    </div>
</div>

</%block>

<%block name="footer">
<script type="text/javascript">
    var myChart = echarts.init(document.getElementById('total_top'));
    myChart.showLoading();

    $.get('/pb.json', function (resp) {
        myChart.hideLoading();
        myChart.setOption(option={
            title: {
                text: "${ctx.get('title')}",
                left: 40,
                textStyle: {"color": "#fff"}
            },
            grid: {left: 20,right: 20},
            textStyle: {"color": "#fff"},
            legend: {
                data:['上证50','沪深300','中证500','中小板指','创业扳指'],
                orient: 'horizontal',
                left: 'center',
                textStyle: {"color": "#fff"}
            },
            toolbox: {left:'right',iconStyle:{borderColor: "#fff"},feature: {saveAsImage: {}}},
            tooltip: {trigger: 'axis'},
            xAxis: {data: resp.map(function (item) {return item[0];})},
            yAxis: {splitLine: {show: true}},
            dataZoom: [{
                type: 'slider',
                borderColor: "#ddd",
                filterMode: 'filter',
                backgroundColor:"rgba(47,69,84,0)",
                fillerColor: "rgba(167,183,204,0.4)",
                startValue: '${ctx.get("start_date")}',
                dataBackground:{
                    areaStyle:{
                        color:['rgba(250,250,250,0.3)'],
                        shadowColor:"red",
                        shadowOffsetX:0,
                        shadowOffsetY:0,
                        shadowBlur:10,
                        opacity:1
                    }
                }
            }, {
            }],
            series: [{
                name: '上证50',
                type: 'line',
                data: resp.map(function (item) {
                    return item[1];
                })
            },{
                name: '沪深300',
                type: 'line',
                data: resp.map(function (item) {
                    return item[2];
                })
            },{
                name: '中证500',
                type: 'line',
                data: resp.map(function (item) {
                    return item[3];
                })
            },{
                name: '中小板指',
                type: 'line',
                data: resp.map(function (item) {
                    return item[4];
                })
            },{
                name: '创业扳指',
                type: 'line',
                data: resp.map(function (item) {
                    return item[5];
                })
            }]
        });

    },dataType="json");
</script>


</%block>
