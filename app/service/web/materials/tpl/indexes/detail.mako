<%inherit file="/_layout/base.mako" />

<%block name="header">
    <link rel="stylesheet" type="text/css" href="/static/css/index.css">
    <title>${ctx.get("index_name")} 估值信息 —— DTGear</title>
</%block>

<%block name="content">
<div class="main-menu" style="background-color: #ffffff99;padding: 10px 50px 80px 50px;">
    <div class="menu-container">
        <h2 class="text-center mgt30 mgb30">
            <a href="#">【${ctx.get("index_name")}】估值信息</a>
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
            <div id="pe_detail" class="main-menu-link thumbnail hq-k-line"> </div>
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
            <div id="pb_detail" class="main-menu-link thumbnail hq-k-line"> </div>
        </div>
    </div>

    <div class="menu-container">
        <div class="col-xs-6 col-md-2" style="background-color: #fff; height: 350px">
            <h3 class="text-capitalize">股息率</h3>
            <ul class="list-unstyled">
                <li>
                    <span class="text-capitalize">当前值:</span>
                    <strong class="text-primary position">${ctx.get("dr_value")}</strong>
                </li>
                <li class="margin-top-30">
                    <span class="text-capitalize">最大值:</span>
                    <strong>${ctx.get("dr_max")}</strong>
                </li>
                <li>
                    <span class="text-capitalize">平均值</span>
                    <strong>${ctx.get("dr_mean")}</strong>
                </li>
                <li>
                    <span class="text-capitalize">最小值:</span>
                    <strong>${ctx.get("dr_min")}</strong>
                </li>
            </ul>
        </div>

        <div class="col-xs-6 col-md-10">
            <div id="dr_detail" class="main-menu-link thumbnail hq-k-line"> </div>
        </div>
    </div>


</div>

</%block>

<%block name="footer">
<script type="text/javascript">
     var dataZoomStyle = [{
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
             }, {}];
     var peChart = echarts.init(document.getElementById('pe_detail'));
     peChart.showLoading();

      $.get('/index/${ctx.get("index_code")}/pe.json', function (resp) {
          peChart.hideLoading();
          peChart.setOption(option={
              legend: {
                  data:['PE-TTM','高位数','中位数','低位数','百分位','收盘点位'],
                  orient: 'horizontal',
                  left: 'center',
                  textStyle: {
                      "color": "#fff"
                  }
              },
              toolbox: {
                  feature: {
                      dataZoom: {
                          yAxisIndex: 'none'
                      },
                      restore: {},
                      saveAsImage: {}
                  }
              },
              tooltip: {trigger: 'axis'},
              textStyle: {"color": "#fff"},
              yAxis: [{name: "PE-TTM", type: "value", splitLine: {show: true}}, {name: "收盘点位", type: "value", splitLine: {show: false}}],
              xAxis: {data: resp.map(function (item) {return item[0];})},
              dataZoom: dataZoomStyle,
              series: [
                  {name: 'PE-TTM',type:'line',color:"#3e7bff",data:resp.map(function (item) {return item[1];})},
                  {name: '高位数',type:'line',color:"#ff001b",data:resp.map(function (item) {return item[2];})},
                  {name: '中位数',type:'line',color:"#fff26a",data:resp.map(function (item) {return item[3];})},
                  {name: '低位数',type:'line',color:"#0bff43",data:resp.map(function (item) {return item[4];})},
                  {name: '百分位',type:'line',color:"#ff04ee",data:resp.map(function (item) {return item[5];})},
                  {name: '收盘点位',type:'line',color:"#ffffff", data:resp.map(function (item) {return item[6];}), yAxisIndex:1, animation: false}
                  ]
          });

      },dataType="json");

     var pbChart = echarts.init(document.getElementById('pb_detail'));
     pbChart.showLoading();

      $.get('/index/${ctx.get("index_code")}/pb.json', function (resp) {
          pbChart.hideLoading();
          pbChart.setOption(option={
              legend: {
                  data:['PB','高位数','中位数','低位数','百分位','收盘点位'],
                  orient: 'horizontal',
                  left: 'center',
                  textStyle: {
                      "color": "#fff"
                  }
              },
              toolbox: {
                  feature: {
                      dataZoom: {
                          yAxisIndex: 'none'
                      },
                      restore: {},
                      saveAsImage: {}
                  }
              },
              tooltip: {trigger: 'axis'},
              textStyle: {"color": "#fff"},
              yAxis: [{name: "PB", type: "value", splitLine: {show: true}}, {name: "收盘点位", type: "value", splitLine: {show: false}}],
              xAxis: {data: resp.map(function (item) {return item[0];})},
              dataZoom: dataZoomStyle,
              series: [
                  {name: 'PB',type:'line',color:"#3e7bff",data:resp.map(function (item) {return item[1];})},
                  {name: '高位数',type:'line',color:"#ff001b",data:resp.map(function (item) {return item[2];})},
                  {name: '中位数',type:'line',color:"#fff26a",data:resp.map(function (item) {return item[3];})},
                  {name: '低位数',type:'line',color:"#0bff43",data:resp.map(function (item) {return item[4];})},
                  {name: '百分位',type:'line',color:"#ff04ee",data:resp.map(function (item) {return item[5];})},
                  {name: '收盘点位',type:'line',color:"#ffffff", data:resp.map(function (item) {return item[6];}), yAxisIndex:1, animation: false}
                  ]
          });

      },dataType="json");


     var drChart = echarts.init(document.getElementById('dr_detail'));
     drChart.showLoading();

      $.get('/index/${ctx.get("index_code")}/dr.json', function (resp) {
          drChart.hideLoading();
          drChart.setOption(option={
              legend: {
                  data:['股息率','收盘点位'],
                  orient: 'horizontal',
                  left: 'center',
                  textStyle: {
                      "color": "#fff"
                  }
              },
              toolbox: {
                  feature: {
                      dataZoom: {
                          yAxisIndex: 'none'
                      },
                      restore: {},
                      saveAsImage: {}
                  }
              },
              tooltip: {trigger: 'axis'},
              textStyle: {"color": "#fff"},
              yAxis: [{name: "股息率", type: "value", splitLine: {show: true}}, {name: "收盘点位", type: "value", splitLine: {show: false}}],
              xAxis: {data: resp.map(function (item) {return item[0];})},
              dataZoom: dataZoomStyle,
              series: [
                  {name: '股息率',type:'line',color:"#3e7bff",data:resp.map(function (item) {return item[1];})},
                  {name: '收盘点位',type:'line',color:"#ffffff", data:resp.map(function (item) {return item[2];}), yAxisIndex:1, animation: false}
                  ]
          });

      },dataType="json");
</script>


</%block>
