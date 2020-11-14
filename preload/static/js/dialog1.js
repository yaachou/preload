'use strict';
  
(function() {
    [].slice.call(document.querySelectorAll('.xd-trigger')).forEach(function(el) {
        el.addEventListener('click', function() {
            let effect = el.getAttribute('data-effect');
            let body = '\
            <div>采用10位数字进行模拟，按照顺序依次为:</div>\
            <div>\
                <div>【地区1位】： 取值范围为1-7，分别代表华北、华南等7个地理区划。</div>\
                <div>【生日8位】： 代表出生年月日，如20010101。</div>\
                <div>【性别1位】： 取值范围为1-2，其中1代表男性，2代表女性。</div>\
            </div>\
            <a>示例号码，仅供参考：1<a style="color:green">20010101</a>2</a>\
            <div style="color:red">【注】：使用电脑端+chrome等浏览器访问效果最佳！</div>\
            <div style="color:red">&emsp;&emsp;&emsp;&emsp;初次访问部分图片加载过慢可通过刷新解决！</div>';

            xdialog.open({
                title: '<b style="color:green">【身份证号码模拟规则】</b>',
                body: body,
                effect: effect,
            });
        });
    });

})();
