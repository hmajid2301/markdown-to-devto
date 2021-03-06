---
title: "Auto Publish React Native App to Android Play Store using GitLab CI"
tags: ["React Native", "CI", "GitLab", "Automation", "Android"]
license: "public-domain"
publish: false
cover_image: https://dev-to-uploads.s3.amazonaws.com/i/w00r4rpmfpjqb8wgygxu.jpg
---

In this article, I will show you how can automate the publishing of your AAB/APK to the `Google Play Console`.
We will be using the [Gradle Play Publisher](https://github.com/Triple-T/gradle-play-publisher) (GPP) plugin to do
automate this process for us. Using this plugin we cannot only automate the publishing and release of our app,
we can also update the release notes, store listing (including photos) all from GitLab CI.

**Note:** In this article I will assume that you are using Linux and React Native version >= 0.60.

![c](c.jpg)
![c](c.jpg)
![c](c.jpg)

[My Blog](/blog/storybooks-with-mdx/)

```py:title=test.png file=./c.py

```

:::caution Assumption
This next section assumes that you use Gitlab to host your repos.
It also assumes that for your Gatsby blog you use Gitlab CI to build/publish it.
:::

---
