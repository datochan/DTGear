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
                left: 'center',
                textStyle: {
                    "color": "#fff"
                }
            },
            textStyle: {
                "color": "#fff"
            },
            legend: {
                data:['上证50','沪深300','中证500','中小板指','创业扳指'],
                orient: 'vertical',
                left: 'right',
                top: 'middle',
                textStyle: {
                    "color": "#fff"
                }
            },
            toolbox: {
                show: true,
                feature: {
                    saveAsImage: {}
                }
            },
            tooltip: {
                trigger: 'axis'
            },
            xAxis: {
                data: resp.map(function (item) {
                    return item[0];
                })
            },
            yAxis: {
                splitLine: {
                    show: true
                }
            },
            dataZoom: [{
                type: 'slider',
                borderColor: "#ddd",
                filterMode: 'filter',
                backgroundColor:"rgba(47,69,84,0)",
                fillerColor: "rgba(167,183,204,0.4)",
                startValue: '${ctx.get("start_date")}',
                dataBackground:{                        //数据阴影的样式。
                    areaStyle:{
                        color:['rgba(250,250,250,0.3)'],//分隔区域颜色。分隔区域会按数组中颜色的顺序依次循环设置颜色。默认是一个深浅的间隔色。
                        shadowColor:"red",          //阴影颜色
                        shadowOffsetX:0,            //阴影水平方向上的偏移距离。
                        shadowOffsetY:0,            //阴影垂直方向上的偏移距离
                        shadowBlur:10,              //图形阴影的模糊大小。
                        opacity:1,                  //图形透明度。支持从 0 到 1 的数字，为 0 时不绘制该图形
                    }
                },
            }, {
            }],
            series: [{
                name: '上证50',
                type: 'line',
                data: resp.map(function (item) {
                    return item[1];
                }),
            },{
                name: '沪深300',
                type: 'line',
                data: resp.map(function (item) {
                    return item[2];
                }),
            },{
                name: '中证500',
                type: 'line',
                data: resp.map(function (item) {
                    return item[3];
                }),
            },{
                name: '中小板指',
                type: 'line',
                data: resp.map(function (item) {
                    return item[4];
                }),
            },{
                name: '创业扳指',
                type: 'line',
                data: resp.map(function (item) {
                    return item[5];
                }),
            },]
        });

    },dataType="json");
</script>


</%block>
