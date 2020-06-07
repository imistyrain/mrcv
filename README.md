# 实用python包

## 配置一键式启用

配置到~/.bashrc中一键式启用

```
alias flops="python ~/opensrc/mrcv/flops.py"
alias http="python ~/opensrc/mrcv/mrhttp.py"
alias gpu="python ~/opensrc/mrcv/gpu.py"
```

## 1. [http.py](http.py) 一款多线程上传下载神器
远程连接服务器开发一般都没有界面，上传下载操作起来就比较繁琐. linux中自带的lz、rz命令虽然可以用于小文件的传输，但是当有上GB的文件进行传输时，时常的挂掉很让人抓狂，好在python中提供了一个简单的httpserver, 仅一行命令就能开启服务器浏览文件，但是其还不支持文件上传功能，真是有点遗憾. 有大拿为其加上了这个功能[SimpleHTTPServerWithUpload](https://github.com/jJayyyyyyy/py3SimpleHTTPServerWithUpload)，可又只支持python, 有好事者将其[移植到了python3下](https://jjayyyyyyy.github.io/2016/10/07/reWrite_SimpleHTTPServerWithUpload_with_python3.html)，但是分成两个文件总感觉不怎么优雅，于是就有了这个一统所有环境的版本.

## 2. [gtop](gtop.py) [一款类似于htop的显卡信息查看工具](https://blog.csdn.net/minstyrain/article/details/99637116?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522159074089619195162560165%2522%252C%2522scm%2522%253A%252220140713.130102334.pc%255Fblog.%2522%257D&request_id=159074089619195162560165&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~blog~first_rank_v1~rank_blog_v1-1-99637116.pc_v1_rank_blog_v1&utm_term=gtop)

```
is_cuda_avaiable 返回是否有GPU可用
get_info 返回具体的GPU任务信息
```
## 3. [image watch](watch.py) OpenCV图像调试工具

VS下有个很好用的插件叫ImageWatch, 可以在调试过程中查看Mat的详细数据，难道python下就没有类似的工具了吗？
答案是No，自己写个不更香嘛.

![watch](watch.png)

## 4. [flops](flops.py) caffe网络计算量统计

flops deploy.prototxt
```
layer name Filter Shape     Output Size      Params   Flops        Ratio
conv1     (96, 3, 11, 11)  (1, 96, 55, 55)  34848    105415200    14.552%
conv2     (256, 48, 5, 5)  (1, 256, 27, 27) 307200   223948800    30.915%
conv3     (384, 256, 3, 3) (1, 384, 13, 13) 884736   149520384    20.64%
conv4     (384, 192, 3, 3) (1, 384, 13, 13) 663552   112140288    15.48%
conv5     (256, 192, 3, 3) (1, 256, 13, 13) 442368   74760192     10.32%
fc6       (4096, 9216)     (1, 4096)        37748736 37748736     5.211%
fc7       (4096, 4096)     (1, 4096)        16777216 16777216     2.316%
fc8       (1000, 4096)     (1, 1000)        4096000  4096000      0.565%
Layers num: 8
Total number of parameters:  60954656
Total number of FLOPs:  724406816
```

## 5. 将caffemodel参数转换为txt可读格式, 适用于仅有caffemodel没有prototxt的情形
由于caffe python端没有导出加载单独caffemodel的接口，用C++实现，需自行编译[caffe](https://github.com/imistyrain/ssd)
```
./build.sh
./modelinfo path_to_caffemodel
```