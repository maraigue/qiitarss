#!/usr/bin/env ruby
# -*- coding: utf-8 -*-

require "cgi"
require "open-uri"
require "time"
require "json"

# ------------------------------------------------------------
# メイン
# ------------------------------------------------------------

module QiitaRSS
module_function
  def h(str)
    CGI.escapeHTML(str)
  end
  
  def load_feed_json(user)
    if user =~ /\\|\/|'/
      raise "無効なユーザ名です。"
    end
    
    `curl 'http://qiita.com/api/v2/users/#{user}/items'`.force_encoding("utf-8")
  end
  
  def view_top
    puts <<HTML
<html>
<head>
<meta http-equiv="content-type" content="text/html;charset=utf-8">
<title>Qiitaの指定ユーザのストック一覧RSS（非公式）</title>
</head>
<body>
<h1>Qiitaの指定ユーザのストック一覧RSS（非公式）</h1>
<form method="GET" action="./" target="_blank"><p>
ユーザ名：<input type="text" name="user">
<input type="submit" value="RSSを取得する">
</p></form>
<hr>
<p>作者：H.Hiro (<a href="main@hhiro.net">e-mail</a>) (<a href="http://qiita.com/h_hiro_">Qiita</a>) (<a href="https://twitter.com/h_hiro_/with_replies">Twitter</a>)</p>
</body>
</html>
HTML
  end
  
  def view_error(text)
    puts <<XML
<?xml version="1.0"?>
<error>#{h text}</error>
XML
  end
  
  def view_json2rss(user)
    buf = nil
    begin
      buf = load_feed_json(user)
    rescue Exception => e
      view_error("フィードを取得できませんでした。(#{h e.class.to_s})")
      return
    end
    
    data = nil
    begin
      data = JSON.load(buf)
    rescue Exception => e
      view_error("フィードのフォーマットが異常です。(#{h e.class.to_s})")
      return
    end
    
    result = <<HEADER
<?xml version="1.0"?>
<rss version="2.0">
  <channel>
    <title>#{h data[0]["user"]["id"]} - Qiita (unofficial RSS)</title>
    <link>"http://qiita.com/#{h data[0]["user"]["id"]}</link>
    <description>#{h data[0]["user"]["id"]}のQiitaへの投稿です。</description>
    <language>ja-jp</language>
HEADER
    begin
      data.each do |d|
        result << <<ITEM
    <item>
      <title>#{h d["title"]}</title>
      <link>#{h d["url"]}</link>
      <description>#{(h d["body"][0, 50])+"..."}</description>
      <pubDate>#{h Time.parse(d["created_at"]).httpdate}</pubDate>
    </item>
ITEM
      end
    rescue Exception => e
      view_error("フィードに必要な情報が揃っていません。(#{h e.class.to_s})")
      return
    end
    result << <<FOOTER
  </channel>
</rss>
FOOTER
    
    puts result
  end
  
  def main
    cgi = CGI.new
    puts cgi.header("text/html; charset=utf-8")
    
    if cgi["user"].to_s != ""
      view_json2rss(cgi["user"])
    else
      view_top
    end
  end
end

QiitaRSS.main
