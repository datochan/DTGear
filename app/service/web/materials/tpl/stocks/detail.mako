<%inherit file="/_layout/base.mako" />

<%block name="header">
    <link rel="stylesheet" type="text/css" href="/static/css/index.css">
    <title>${ctx.get("stock_name")} 估值信息 —— DTGear</title>
</%block>

<%block name="content">
    <div class="main-menu" style="background-color: #ffffff99;padding: 10px 50px 80px 50px;">
        <div class="menu-container">
            <h2 class="text-center mgt30 mgb30">
                <a href="#">【${ctx.get("stock_name")}】估值信息</a>
            </h2>
        </div>

        <div class="menu-container">
            <div class="col-xs-6 col-md-2" style="background-color: #fff; height: 350px">
                <h3 class="text-capitalize">滚动市盈率</h3>
                <ul class="list-unstyled">
                    <li>
                        <span class="text-capitalize">当前值:</span>
                        <strong class="text-primary position">${ctx.get("pe_value")}</strong>
                    </li>
                    <li class="ng-scope">
                        <span class="text-capitalize">百分位</span>
                        <strong class="text-primary position">${ctx.get("pe_rate")}</strong>
                    </li>
                    <li class="ng-scope">
                        <span class="text-capitalize">高位数</span>
                        <strong class="val text-danger">${ctx.get("pe_high")}</strong>
                    </li>
                    <li class="ng-scope">
                        <span class="text-capitalize">中位数</span>
                        <strong>${ctx.get("pe_middle")}</strong>
                    </li>
                    <li class="ng-scope">
                        <span class="text-capitalize">低位数</span>
                        <strong class="val text-success">${ctx.get("pe_low")}</strong>
                    </li>
                    <li class="margin-top-30">
                        <span class="text-capitalize">最大值:</span>
                        <strong>${ctx.get("pe_max")}</strong>
                    </li>
                    <li>
                        <span class="text-capitalize">平均值</span>
                        <strong>${ctx.get("pe_mean")}</strong>
                    </li>
                    <li>
                        <span class="text-capitalize">最小值:</span>
                        <strong>${ctx.get("pe_min")}</strong>
                    </li>
                </ul>
            </div>

            <div class="col-xs-6 col-md-10">
                <div id="pe_detail" class="main-menu-link thumbnail hq-k-line"></div>
            </div>
        </div>

        <div class="menu-container">
            <div class="col-xs-6 col-md-2" style="background-color: #fff; height: 350px">
                <h3 class="text-capitalize">市净率</h3>
                <ul class="list-unstyled">
                    <li>
                        <span class="text-capitalize">当前值:</span>
                        <strong class="text-primary position">${ctx.get("pb_value")}</strong>
                    </li>
                    <li class="ng-scope">
                        <span class="text-capitalize">百分位</span>
                        <strong class="text-primary position">${ctx.get("pb_rate")}</strong>
                    </li>
                    <li class="ng-scope">
                        <span class="text-capitalize">高位数</span>
                        <strong class="val text-danger">${ctx.get("pb_high")}</strong>
                    </li>
                    <li class="ng-scope">
                        <span class="text-capitalize">中位数</span>
                        <strong>${ctx.get("pb_middle")}</strong>
                    </li>
                    <li class="ng-scope">
                        <span class="text-capitalize">低位数</span>
                        <strong class="val text-success">${ctx.get("pb_low")}</strong>
                    </li>
                    <li class="margin-top-30">
                        <span class="text-capitalize">最大值:</span>
                        <strong>${ctx.get("pb_max")}</strong>
                    </li>
                    <li>
                        <span class="text-capitalize">平均值</span>
                        <strong>${ctx.get("pb_mean")}</strong>
                    </li>
                    <li>
                        <span class="text-capitalize">最小值:</span>
                        <strong>${ctx.get("pb_min")}</strong>
                    </li>
                </ul>
            </div>

            <div class="col-xs-6 col-md-10">
                <div id="pb_detail" class="main-menu-link thumbnail hq-k-line"></div>
            </div>
        </div>
    </div>

</%block>

<%block name="footer">
    <script type="text/javascript">
        var allDataIcon = 'path://M925.0304 82.3808c-25.4464-16.6912-61.0816-31.488-105.9328-43.9296-89.1904-24.7808-207.36-38.4-332.6976-38.4s-243.5072 13.6704-332.6976 38.4c-44.9024 12.4416-80.5376 27.2384-105.9328 43.9296-31.6928 20.8384-47.7696 44.7488-47.7696 71.2192l0 614.4c0 26.4704 16.0768 50.432 47.7696 71.2192 25.4464 16.6912 61.0816 31.488 105.9328 43.9296 89.1904 24.7808 207.36 38.4 332.6976 38.4s243.5072-13.6704 332.6976-38.4512c44.9024-12.4416 80.5376-27.2384 105.9328-43.9296 31.6928-20.7872 47.7696-44.7488 47.7696-71.2192l0-614.4c0-26.4704-16.0768-50.432-47.7696-71.2192zM167.424 87.7568c84.8896-23.552 198.144-36.5568 318.976-36.5568s234.1376 13.0048 318.976 36.5568c91.904 25.5488 116.224 54.2208 116.224 65.8432s-24.2688 40.2944-116.224 65.8432c-84.8896 23.552-198.144 36.5568-318.976 36.5568s-234.1376-13.0048-318.976-36.5568c-91.904-25.5488-116.224-54.2208-116.224-65.8432s24.2688-40.2944 116.224-65.8432zM805.376 833.8432c-84.8896 23.552-198.144 36.5568-318.976 36.5568s-234.1376-13.0048-318.976-36.5568c-91.904-25.5488-116.224-54.2208-116.224-65.8432l0-131.3792c25.1904 15.8208 59.5968 29.8496 102.5024 41.7792 89.1904 24.7808 207.36 38.4 332.6976 38.4s243.5072-13.6704 332.6976-38.4512c42.9056-11.9296 77.3632-25.9584 102.5024-41.7792l0 131.3792c0 11.6224-24.2688 40.2944-116.224 65.8432zM805.376 629.0432c-84.8896 23.552-198.144 36.5568-318.976 36.5568s-234.1376-13.0048-318.976-36.5568c-91.904-25.5488-116.224-54.2208-116.224-65.8432l0-131.3792c25.1904 15.8208 59.5968 29.8496 102.5024 41.7792 89.1904 24.7808 207.36 38.4 332.6976 38.4s243.5072-13.6704 332.6976-38.4c42.9056-11.9296 77.3632-25.9584 102.5024-41.7792l0 131.3792c0 11.6224-24.2688 40.2944-116.224 65.8432zM805.376 424.2432c-84.8896 23.552-198.144 36.5568-318.976 36.5568s-234.1376-13.0048-318.976-36.5568c-91.904-25.5488-116.224-54.2208-116.224-65.8432l0-131.3792c25.1904 15.8208 59.5968 29.8496 102.5024 41.7792 89.1904 24.7808 207.36 38.4 332.6976 38.4s243.5072-13.6704 332.6976-38.4c42.9056-11.9296 77.3632-25.9584 102.5024-41.7792l0 131.3792c0 11.6224-24.2688 40.2944-116.224 65.8432z';
        var tenYearsDataIcon = 'path://M863.328 482.56l-317.344-1.12L545.984 162.816c0-17.664-14.336-32-32-32s-32 14.336-32 32l0 318.4L159.616 480.064c-0.032 0-0.064 0-0.096 0-17.632 0-31.936 14.24-32 31.904C127.424 529.632 141.728 544 159.392 544.064l322.592 1.152 0 319.168c0 17.696 14.336 32 32 32s32-14.304 32-32l0-318.944 317.088 1.12c0.064 0 0.096 0 0.128 0 17.632 0 31.936-14.24 32-31.904C895.264 496.992 880.96 482.624 863.328 482.56z';

        var dataZoomStyle = [{
            type: 'slider',
            borderColor: "#ddd",
            filterMode: 'filter',
            backgroundColor: "rgba(47,69,84,0)",
            fillerColor: "rgba(167,183,204,0.4)",
            startValue: '${ctx.get("start_date")}',
            dataBackground: {
                areaStyle: {
                    color: ['rgba(250,250,250,0.3)'],
                    shadowColor: "red",
                    shadowOffsetX: 0,
                    shadowOffsetY: 0,
                    shadowBlur: 10,
                    opacity: 1
                }
            }
        }, {}];


        var peChart = echarts.init(document.getElementById('pe_detail'));

        function reloadPEChart(all) {
            var pe_url = "/stock/${ctx.get("stock_code")}/pe.json";
            if (all) {
                pe_url += "?all=1"
            }
            peChart.showLoading();

            $.get(pe_url, function (resp) {
                peChart.hideLoading();
                peChart.setOption(option = {
                    legend: {
                        data: ['PE-TTM', '高位数', '中位数', '低位数', '百分位', '收盘点位'],
                        orient: 'horizontal',
                        left: 'center',
                        textStyle: {
                            "color": "#fff"
                        }
                    },
                    grid: {left: 50, right: 50},
                    toolbox: {
                        left: 'right',
                        iconStyle: {borderColor: "#fff"},
                        feature: {
                            myAll: { title: '所有数据',icon: allDataIcon, onclick: function () { reloadPEChart(true); } },
                            myTenYears: {title:'近十年数据',icon: tenYearsDataIcon,onclick:function(){ reloadPEChart();}},
                            saveAsImage: {}
                        }
                    },
                    tooltip: {trigger: 'axis', axisPointer: { type: 'cross' }},
                    textStyle: {"color": "#fff"},
                    yAxis: [{name: "PE-TTM", type: "value", splitLine: {show: true}},
                        {name: "收盘点位",type: "value",splitLine: {show: false}}],
                    xAxis: {data: resp.map(function (item) {return item[0];})},
                    dataZoom: dataZoomStyle,
                    series: [
                        {
                            name: 'PE-TTM', type: 'line', color: "#3e7bff", data: resp.map(function (item) {
                                return item[1];
                            })
                        },
                        {
                            name: '高位数', type: 'line', color: "#ff001b", data: resp.map(function (item) {
                                return item[2];
                            })
                        },
                        {
                            name: '中位数', type: 'line', color: "#fff26a", data: resp.map(function (item) {
                                return item[3];
                            })
                        },
                        {
                            name: '低位数', type: 'line', color: "#0bff43", data: resp.map(function (item) {
                                return item[4];
                            })
                        },
                        {
                            name: '百分位', type: 'line', color: "#ff04ee", data: resp.map(function (item) {
                                return item[5];
                            })
                        },
                        {
                            name: '收盘点位', type: 'line', color: "#ffffff", data: resp.map(function (item) {
                                return item[6];
                            }), yAxisIndex: 1, animation: false
                        }
                    ]
                });

            }, "json");

        }


        var pbChart = echarts.init(document.getElementById('pb_detail'));
        function reloadPBChart(all) {
            var pb_url = "/stock/${ctx.get("stock_code")}/pb.json";
            if (all) {
                pb_url += "?all=1"
            }
            pbChart.showLoading();

            $.get(pb_url, function (resp) {
                pbChart.hideLoading();
                pbChart.setOption(option = {
                    legend: {
                        data: ['PB', '高位数', '中位数', '低位数', '百分位', '收盘点位'],
                        orient: 'horizontal',
                        left: 'center',
                        textStyle: {
                            "color": "#fff"
                        }
                    },
                    grid: {left: 50, right: 50},
                    toolbox: {
                        left: 'right',
                        iconStyle: {borderColor: "#fff"},
                        feature: {
                            myAll: { title: '所有数据',icon: allDataIcon, onclick: function () { reloadPBChart(true); } },
                            myTenYears: {title:'近十年数据',icon: tenYearsDataIcon,onclick:function(){ reloadPBChart();}},
                            saveAsImage: {}
                        }
                    },
                    tooltip: {trigger: 'axis', axisPointer: { type: 'cross' }},
                    textStyle: {"color": "#fff"},
                    yAxis: [{name: "PB", type: "value", splitLine: {show: true}}, {
                        name: "收盘点位",
                        type: "value",
                        splitLine: {show: false}
                    }],
                    xAxis: {
                        data: resp.map(function (item) {
                            return item[0];
                        })
                    },
                    dataZoom: dataZoomStyle,
                    series: [
                        {
                            name: 'PB', type: 'line', color: "#3e7bff", data: resp.map(function (item) {
                                return item[1];
                            })
                        },
                        {
                            name: '高位数', type: 'line', color: "#ff001b", data: resp.map(function (item) {
                                return item[2];
                            })
                        },
                        {
                            name: '中位数', type: 'line', color: "#fff26a", data: resp.map(function (item) {
                                return item[3];
                            })
                        },
                        {
                            name: '低位数', type: 'line', color: "#0bff43", data: resp.map(function (item) {
                                return item[4];
                            })
                        },
                        {
                            name: '百分位', type: 'line', color: "#ff04ee", data: resp.map(function (item) {
                                return item[5];
                            })
                        },
                        {
                            name: '收盘点位', type: 'line', color: "#ffffff", data: resp.map(function (item) {
                                return item[6];
                            }), yAxisIndex: 1, animation: false
                        }
                    ]
                });

            }, "json");
        }

        reloadPEChart();
        reloadPBChart();
    </script>


</%block>
