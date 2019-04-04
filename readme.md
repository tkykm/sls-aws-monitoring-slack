# AWSの監視系のサービスのデプロイと通知までを設定する

AWSの監視系のサービスの設定とSlack通知を設定するserverless frameworkのコードです。
サービス毎にスタックを分けているので、自分の環境に合っていると思ったものだけデプロイしてください。

## 対象サービス

| name | category | memo
|:-----------|:------------|:--|
| GuardDuty | region service | slsが関連リソースを全て作成. eu-north-1が非対応
| Trusted Advisor| global service | Trusted Advisor自体の設定はslsで行わない。別途手動でビジネスサポートに加入などする.
| Config| region service | slsが関連リソースを全て作成
| Inspector| region service| slsが関連リソースを全て作成. 一部リージョンのみ対応
| Budget| global service| slsが関連リソースを全て作成
| Macie| reion service| 今回対象外

## 構成イメージ

![](https://s3-ap-northeast-1.amazonaws.com/hackmd-jp1/uploads/upload_e28bbac0df692ab24ff5eb81970a6041.png)

## 設定ファイル

デプロイする前に、`cp config/config.yml.sample config/config.yml`を実行して、
config.ymlファイルを作成し、内容を適宜編集してください。

| name | required| value| sample
|:-----------|:--|:------------|:------------|
PREFIX_SERVICE_NAME| yes |slsのサービス名のプレフィックス| projectname
PREFIX_S3| yes| serverless frameworkで使用するartifactなどを置くS3のバケット名のプレフィックス | projectname
STACK_TAGS| yes| CloudFormationに設定されるタグ。作成されるすべてのリソースにこのタグがつけられる| key1: value1<br>key2: value2
WEBHOOK_URLS| yes |デフォルトのSlackのincoming webhookのURL. カンマ区切りで複数設定可能| https://hooks.slack.com/services/hogehoge/fugaugau/tokentokne,https://hooks.slack.com/services/fooooooooo/fugaugau/tokentokn
WEBHOOK_URLS_INSPECTOR| no |Inspector通知用のSlackのincoming webhookのURL. 省略した場合、WEBHOOK_URLSの値が使用される.カンマ区切りで複数設定可能| https://hooks.slack.com/services/hogehoge/fugaugau/tokentokne,https://hooks.slack.com/services/fooooooooo/fugaugau/tokentokn
WEBHOOK_URLS_CONFIG| no |Config通知用のSlackのincoming webhookのURL. 省略した場合、WEBHOOK_URLSの値が使用される.カンマ区切りで複数設定可能| https://hooks.slack.com/services/hogehoge/fugaugau/tokentokne,https://hooks.slack.com/services/fooooooooo/fugaugau/tokentokn
WEBHOOK_URLS_TRUSTEDADVISOR| no |Trusted Advisor通知用のSlackのincoming webhookのURL. 省略した場合、WEBHOOK_URLSの値が使用される.カンマ区切りで複数設定可能| https://hooks.slack.com/services/hogehoge/fugaugau/tokentokne,https://hooks.slack.com/services/fooooooooo/fugaugau/tokentokn
WEBHOOK_URLS_BUDGET| no |Budget通知用のSlackのincoming webhookのURL. 省略した場合、WEBHOOK_URLSの値が使用される.カンマ区切りで複数設定可能| https://hooks.slack.com/services/hogehoge/fugaugau/tokentokne,https://hooks.slack.com/services/fooooooooo/fugaugau/tokentokn
WEBHOOK_URLS_GUARDDUTY| no |GuardDuty通知用のSlackのincoming webhookのURL. 省略した場合、WEBHOOK_URLSの値が使用される.カンマ区切りで複数設定可能| https://hooks.slack.com/services/hogehoge/fugaugau/tokentokne,https://hooks.slack.com/services/fooooooooo/fugaugau/tokentokn
BUDGET_LIMIT| yes(Budgetをデプロイしない場合不要) |USDで月の予算| 1000
BUDGET_TAGKEYVALUE| yes(Budgetをデプロイしない場合不要) |料金のフィルタ. タグの配列で指定| - "user:key1\$value1"<br>- "user:key2$value2"
BUDGET_THRESHOLD_PERCENTAGE| yes(Budgetをデプロイしない場合不要) | アラートを出す予算のしきい値(%).月の予想料金が予算のしきい値を超えるとSlack通知される| 80


## deploy

### common
serverless frameworkやaws cliのインストールがまだの方は以下のpre-requisitesを完了させてください。
https://serverless.com/framework/docs/providers/aws/guide/quick-start/#pre-requisites

### GuardDuty
GuardDutyはregionサービスなので監視したいリージョンにslsをデプロイする。
以下は全リージョンにデプロイする例
```
$ cd guardduty
$ aws ec2 describe-regions  | jq '.Regions[].RegionName' | xargs -n 1 -J % sls deploy  --region %
```
すでにguarddutyがデプロイ（有効）されている場合は、以下のオプションを付けて実行
You can use below If you only deploy service(lamnda, IAM role) 
```
$ cd guardduty
$ npm install --save serverless-plugin-additional-stacks
$ sls deploy  --skip-additionalstacks
```
![](https://s3-ap-northeast-1.amazonaws.com/hackmd-jp1/uploads/upload_145e3836937455b7595e77849a025b06.png)


### Trusted Advisor
trusted advisor自体は別途手動で有効にする。
無料版でも動作する（はず）。
us-east-1にのみデプロイする。

```
$ cd trustedadvisor
$ sls deploy  --region us-east-1
```
![](https://s3-ap-northeast-1.amazonaws.com/hackmd-jp1/uploads/upload_e49728caafcd0c6171ba2d4b9905a704.png)


### Config
regionサービスなので監視したいリージョンにデプロイする.
サービスの変更状態を記録するレコーダとdelivery channelはリージョンに1つまでしか作成できないので、すでに作成している場合は、リソースを削除するか、serverless.ymlからConfigRecorderとDeliveryChannelに関する記述を削除する。
us-east-1リージョンでのみ、IAMなどのグローバルリソースも対象としたレコーディングを行う。
このリージョンを変えたければ、以下の部分のリージョン名を変える.
```
custom:
  globalresourcesupport:
    us-east-1: true
```

```
$ cd awsconfig
$ aws ec2 describe-regions  | jq '.Regions[].RegionName' | xargs -n 1 -J % sls deploy  --region %
```
![](https://s3-ap-northeast-1.amazonaws.com/hackmd-jp1/uploads/upload_864376521bbe7739c8ce6d837c2e6ed9.png)

### Inspector
regionサービスなので監視したいリージョンにデプロイする.
デプロイされたリージョンのすべてのインスタンスを対象にNetwork Reachability-1.1の評価が実施される（1週間に1回）

以下Inspectorが対応している全リージョンにデプロイする例
```
$ cd inspector
$ for region in us-east-1 us-east-2 us-west-1 us-west-2 ap-south-1 ap-southeast-2 ap-northeast-2 ap-northeast-1 eu-west-1 eu-central-1; do sls deploy --aws-profile ss --region $region; done
```

![](https://s3-ap-northeast-1.amazonaws.com/hackmd-jp1/uploads/upload_df0d39ed79239df0ae5ba10fa73ab6dd.png)


### Budget

config.ymlのBUDGET_LIMIT, BUDGET_THRESHOLD_PERCENTAGE, BUDGET_TAGKEYVALUEの値を予め自分のものに変更しておく. 
BUDGET_LIMITの単位はUSD.
tagkeyは以下のように複数設定可能

```
BUDGET_TAGKEYVALUE:
  - "user:key1$value1"
  - "user:key2$value2"
```

もしタグでフィルタしない場合、誰も使用していないタグ名で値を空に設定する
```
BUDGET_TAGKEYVALUE:
  - "user:keynobodyuse$"
```

グローバルサービスなので、us-east-1にのみデプロイする
```
cd budget
sls deploy  --region us-east-1
```
![](https://s3-ap-northeast-1.amazonaws.com/hackmd-jp1/uploads/upload_24e3cc506a5482ecf02e30b677b642de.png)


## 各サービスの設定

なお、ほぼすべてのlambdaはtry except等していません。何かエラー起きたらcloudwatchで見ればいいやという考えです

### GuardDuty
GuardDuty Detectorが検知する内容をすべてSlack通知する。
severityが4以上のものはhere, 7以上のものにはchannelメンションをつける。
グローバルサービス（IAM等）に関することを検知した場合、全リージョンから同一の内容がSlack通知されてしまう。

### Trusted Advisor

状態がERRORとなっているものをSlack通知する。
WARNも出したい場合は、trustedadvisor/serverless.ymlでERRORと書かれているところを以下のように編集する.
```
detail:
  status:
    - ERROR
    - WARN
```

無視したい項目があってもTrusted Advisor側で無視できる方法がない為、
無視したいイベントが合った場合、lambdaを編集する。



### Config
すべての変更イベントをトリガーとして、変更があったこと、変更内容を通知する.
イベントタイプとしてConfigurationItemChangeNotificationに反応する.
OversizedConfigurationItemChangeNotificationはトリガーされるが、lambdaで無視する.
recordVersion: 1.3で作っている
configurationItemDiff, configurationItemがあるものだけSlack通知する.

#### なぜそうしているか
コストを抑える為.
aws configはリソースの状態をs3に記録しておいて、何かリソースが変更された時にAWSが用意している評価関数か、オリジナル関数を実行できるというもの.
2019/3/25現在、AWSが管理する評価関数は83個あり、GuarddutyやTrusted Advisorなどと重複しているものも複数存在している.
Configの課金体系は以下で参照できる.https://aws.amazon.com/config/pricing
初期費としてリソースの数 * $0.003がまず掛かる.これは比較的リーズナブルだと思う.
そしてランニング費用として、アクティブなルール(評価関数)の数につき$1~2掛かる.
つまり、全リージョンで全部有効化すると、(10 * $2 + 40 * $1.5 + 33 * $1) * 16 = $1808/month
そこで、何かしらの変更があったことだけ通知するカスタム関数の実行だけにすることで、ルール数課金を$32/month($2 * 16)にすることができる.
AWSのマネージドルールの場合は、Lambdaの料金は発生しないが、カスタムルールの場合はLamndaの料金が発生する.
今回のLambdaのおおよそ1回あたりの実行時間は600ms. 128memoryでのms単金は0.000000208USDなので、1日に1000回構成変更があるとしたら、
0.000000208 * 600 * 1000 * 30 = $3.744/month

#### 今後

すべてのイベントが通知されても見きれない為、IAMのイベントだけ通知する等のチューニングを行っていく

### Inspector
ターゲットとして全てのEC2、エージェントインストールなしとする.
評価テンプレートでは、Network Reachability-1.1のルールパッケージを使っている.

cloudwatch eventでも拾えるがが、イベントのフィルタ方法が謎なので、SNS経由とする。
評価完了時にSNSへPublishされる。

2019/03/26で以下のリージョンに対応している
Govはテストできないので、今回のslsはGovには対応していない。

Asia Pacific (Mumbai)
Asia Pacific (Seoul)
Asia Pacific (Sydney)
Asia Pacific (Tokyo)
EU (Frankfurt)
EU (Ireland)
US East (Northern Virginia)
US East (Ohio)
US West (Northern California)
US West (Oregon)
AWS GovCloud (US-East)
AWS GovCloud (US-West)

それぞれのリージョンでルールセットのARNが決まっている.
今回は以下ARNをserverless.ymlにハードコードしている.

|region| Network Reachability rule package arn
|:-----------|:------------|
|us-east-1| arn:aws:inspector:us-east-1:316112463485:rulespackage/0-PmNV0Tcd
|us-east-2| arn:aws:inspector:us-east-2:646659390643:rulespackage/0-cE4kTR30
|us-west-1|arn:aws:inspector:us-west-1:166987590008:rulespackage/0-TxmXimXF
|us-west-2|arn:aws:inspector:us-west-2:758058086616:rulespackage/0-rD1z6dpl
|ap-south-1|arn:aws:inspector:ap-south-1:162588757376:rulespackage/0-YxKfjFu1
|ap-southeast-2|arn:aws:inspector:ap-southeast-2:454640832652:rulespackage/0-FLcuV4Gz
|ap-northeast-2|arn:aws:inspector:ap-northeast-2:526946625049:rulespackage/0-s3OmLzhL
|ap-northeast-1|arn:aws:inspector:ap-northeast-1:406045910587:rulespackage/0-YI95DVd7
|eu-west-1|arn:aws:inspector:eu-west-1:357557129151:rulespackage/0-SPzU33xe
|eu-central-1|arn:aws:inspector:eu-central-1:537503971621:rulespackage/0-6yunpJ91

これ以外のリージョンを指定してデプロイした場合、失敗する

NetworkExposureについてSlack通知する. infoレベルなので特にメンションはつけない.

CloudFormationがinspectorのSNS設定に対応していないので、
SNSトピックの設定をするlambdaをカスタムリソースとして呼び出している.
評価完了時にSNSに結果が通知されるが、findingsのarnまでしか得られないので、そこから評価詳細を取得してSlack通知している.

#### Pricing
1回の実行に0.15〜0.04USD(従量制割引)
1週間に1回実行するので、全リージョンでVMが100あった場合、
250 * 0.15 + 150 * 0.13 = 57 USD/28day

### Budget
BUDGET_LIMITに設定した数値を月の予算（USD）としたBudgetが作成される。
BUDGET_TAGKEYVALUEで指定したタグでフィルタされたものが実料金として計算される.h
コスト予想 > BUDGET_LIMIT * BUDGET_THRESHOLD_PERCENTAGE/100となった際にSlack通知される.


### Macie
aws macieは、s3にある個人情報などのデータを自動認識し、そのデータへのアクセス状況などをモニタリングできるサービス。
料金が高いので、今回は見送った。
対象のs3のデータ量(全バケットが対象) * $5/GB/month + 解析料金が掛かる.
データは更新分や追加分にのみ翌月追加で課金される。解析料金はデータ料金0.5くらいみておけばいい
https://aws.amazon.com/macie/pricing/

