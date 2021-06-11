from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class AdvUser(AbstractUser):
    """Расширенная модель пользователя"""

    username = models.CharField(max_length=20, verbose_name='Имя пользователя', unique=True)
    avatar = models.ImageField(verbose_name='Аватар', null=True, blank=True, )
    is_activated = models.BooleanField(verbose_name='Подтверждена эл. почта?', default=False)

    COUNTRIES = (
        ('1', 'Абхазия'),
        ('2', 'Австралия'),
        ('3', 'Австрия'),
        ('4', 'Азербайджан'),
        ('5', 'Албания'),
        ('6', 'Алжир'),
        ('7', 'Ангола'),
        ('8', 'Андорра'),
        ('9', 'Антигуа и Барбуда'),
        ('10', 'Аргентина'),
        ('11', 'Армения'),
        ('12', 'Афганистан'),
        ('13', 'Багамские Острова'),
        ('14', 'Бангладеш'),
        ('15', 'Барбадос'),
        ('16', 'Бахрейн'),
        ('17', 'Белиз'),
        ('18', 'Белоруссия'),
        ('19', 'Бельгия'),
        ('20', 'Бенин'),
        ('21', 'Болгария'),
        ('22', 'Боливия'),
        ('23', 'Босния и Герцеговина'),
        ('24', 'Ботсвана'),
        ('25', 'Бразилия'),
        ('26', 'Бруней'),
        ('27', 'Буркина-Фасо'),
        ('28', 'Бурунди'),
        ('29', 'Бутан'),
        ('30', 'Вануату'),
        ('31', 'Ватикан'),
        ('32', 'Великобритания'),
        ('33', 'Венгрия'),
        ('34', 'Венесуэла'),
        ('35', 'Восточный Тимор'),
        ('36', 'Вьетнам'),
        ('37', 'Габон'),
        ('38', 'Гаити'),
        ('39', 'Гайана'),
        ('40', 'Гамбия'),
        ('41', 'Гана'),
        ('42', 'Гватемала'),
        ('43', 'Гвинея'),
        ('44', 'Гвинея-Бисау'),
        ('45', 'Германия'),
        ('46', 'Гондурас'),
        ('47', 'Государство Палестина'),
        ('48', 'Гренада'),
        ('49', 'Греция'),
        ('50', 'Грузия'),
        ('51', 'Дания'),
        ('52', 'Джибути'),
        ('53', 'Доминика'),
        ('54', 'Доминиканская Республика'),
        ('55', 'ДР Конго'),
        ('56', 'Египет'),
        ('57', 'Замбия'),
        ('58', 'Зимбабве'),
        ('59', 'Израиль'),
        ('60', 'Индия'),
        ('61', 'Индонезия'),
        ('62', 'Иордания'),
        ('63', 'Ирак'),
        ('64', 'Иран'),
        ('65', 'Ирландия'),
        ('66', 'Исландия'),
        ('67', 'Испания'),
        ('68', 'Италия'),
        ('69', 'Йемен'),
        ('70', 'Кабо-Верде'),
        ('71', 'Казахстан'),
        ('72', 'Камбоджа'),
        ('73', 'Камерун'),
        ('74', 'Канада'),
        ('75', 'Катар'),
        ('76', 'Кения'),
        ('77', 'Кипр'),
        ('78', 'Киргизия'),
        ('79', 'Кирибати'),
        ('80', 'Китай'),
        ('81', 'КНДР'),
        ('82', 'Колумбия'),
        ('84', 'Коморские Острова'),
        ('85', 'Коста-Рика'),
        ('86', "Кот-д'Ивуар"),
        ('87', 'Куба'),
        ('88', 'Кувейт'),
        ('89', 'Лаос'),
        ('90', 'Латвия'),
        ('91', 'Лесото'),
        ('92', 'Либерия'),
        ('93', 'Ливан'),
        ('94', 'Ливия'),
        ('95', 'Литва'),
        ('96', 'Лихтенштейн'),
        ('97', 'Люксембург'),
        ('98', 'Маврикий'),
        ('99', 'Мавритания'),
        ('101', 'Мадагаскар'),
        ('102', 'Малави'),
        ('103', 'Малайзия'),
        ('104', 'Мали'),
        ('105', 'Мальдивские Острова'),
        ('106', 'Мальта'),
        ('107', 'Марокко'),
        ('108', 'Маршалловы Острова'),
        ('109', 'Мексика'),
        ('110', 'Мозамбик'),
        ('111', 'Молдавия'),
        ('112', 'Монако'),
        ('113', 'Монголия'),
        ('114', 'Мьянма'),
        ('115', 'Намибия'),
        ('116', 'Науру'),
        ('117', 'Непал'),
        ('118', 'Нигер'),
        ('119', 'Нигерия'),
        ('120', 'Нидерланды'),
        ('121', 'Никарагуа'),
        ('122', 'Новая Зеландия'),
        ('123', 'Норвегия'),
        ('124', 'ОАЭ'),
        ('125', 'Оман'),
        ('126', 'Пакистан'),
        ('127', 'Палау'),
        ('128', 'Панама'),
        ('129', 'Папуа - Новая Гвинея'),
        ('130', 'Парагвай'),
        ('131', 'Перу'),
        ('132', 'Польша'),
        ('133', 'Португалия'),
        ('134', 'Республика Конго'),
        ('135', 'Республика Корея'),
        ('136', 'Россия'),
        ('137', 'Руанда'),
        ('138', 'Румыния'),
        ('139', 'Сальвадор'),
        ('140', 'Самоа'),
        ('141', 'Сан-Марино'),
        ('142', 'Сан-Томе и Принсипи'),
        ('143', 'Саудовская Аравия'),
        ('144', 'Северная Македония'),
        ('145', 'Сейшельские Острова'),
        ('146', 'Сенегал'),
        ('147', 'Сент-Винсент и Гренадины'),
        ('148', 'Сент-Китс и Невис'),
        ('149', 'Сент-Люсия'),
        ('150', 'Сербия'),
        ('151', 'Сингапур'),
        ('152', 'Сирия'),
        ('153', 'Словакия'),
        ('154', 'Словения'),
        ('155', 'Соломоновы Острова'),
        ('156', 'Сомали'),
        ('157', 'Судан'),
        ('158', 'Суринам'),
        ('159', 'США'),
        ('160', 'Сьерра-Леоне'),
        ('161', 'Таджикистан'),
        ('162', 'Таиланд'),
        ('163', 'Танзания'),
        ('164', 'Того'),
        ('165', 'Тонга'),
        ('166', 'Тринидад и Тобаго'),
        ('167', 'Тувалу'),
        ('168', 'Тунис'),
        ('169', 'Туркмения'),
        ('170', 'Турция'),
        ('171', 'Уганда'),
        ('172', 'Узбекистан'),
        ('173', 'Украина'),
        ('174', 'Уругвай'),
        ('175', 'Федеративные Штаты Микронезии'),
        ('176', 'Фиджи'),
        ('177', 'Филиппины'),
        ('178', 'Финляндия'),
        ('179', 'Франция'),
        ('180', 'Хорватия'),
        ('181', 'ЦАР'),
        ('182', 'Чад'),
        ('183', 'Черногория'),
        ('184', 'Чехия'),
        ('185', 'Чили'),
        ('186', 'Швейцария'),
        ('187', 'Швеция'),
        ('188', 'Шри-Ланка'),
        ('189', 'Эквадор'),
        ('190', 'Экваториальная Гвинея'),
        ('191', 'Эритрея'),
        ('192', 'Эсватини'),
        ('193', 'Эстония'),
        ('194', 'Эфиопия'),
        ('195', 'ЮАР'),
        ('196', 'Южная Осетия'),
        ('197', 'Южный Судан'),
        ('198', 'Ямайка'),
        ('199', 'Япония'),
    )

    country = models.CharField(verbose_name='Страна', choices=COUNTRIES, max_length=50, null=True, blank=True)
    phone = models.CharField(verbose_name='Номер телефона', null=True, blank=True, max_length=12)
    birthday = models.DateField(verbose_name='Дата рождения', null=True, blank=True)
    private = models.BooleanField(verbose_name='Приватный аккаунт', default=False)
    views = models.IntegerField(verbose_name='Количество просмотров', default=0)
    likes = models.ManyToManyField('Article', verbose_name='Понравившиеся статьи', blank=True)
    aboutUser = models.TextField(verbose_name='О пользователе', null=True, blank=True)
    publications = models.IntegerField(verbose_name='Публикации', default=0)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)


class Subscribe(models.Model):
    """Модель подписки"""

    user = models.PositiveIntegerField(verbose_name='ID пользователя')
    subscribers = models.ManyToManyField(AdvUser, verbose_name='Подписчики', blank=True)

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписчики'


class Rubric(models.Model):
    """Модель рубрики"""

    rubric_name = models.CharField(verbose_name='Название рубрики', max_length=50)

    def __str__(self):
        return self.rubric_name

    class Meta:
        verbose_name = 'Рубрика'
        verbose_name_plural = 'Рубрики'


class Article(models.Model):
    """Модель статьи"""

    title = models.CharField(verbose_name='Название статьи', max_length=50)
    content = models.TextField(verbose_name='Содержание статьи')
    rubric = models.ForeignKey(Rubric, verbose_name='Рубрика', on_delete=models.PROTECT)
    pub_date = models.DateTimeField(verbose_name='Дата публикации', auto_now_add=True)
    author = models.ForeignKey(AdvUser, on_delete=models.CASCADE, verbose_name='Автор статьи')
    image = models.ImageField(verbose_name='Изображение', null=True, blank=True)
    views = models.IntegerField(verbose_name='Количество просмотров', default=0)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
        ordering = ('-pub_date',)


class Comment(models.Model):
    """Модель комментариев"""

    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name='Статья')
    author = models.ForeignKey(AdvUser, on_delete=models.CASCADE, verbose_name='Автор комментария', max_length=50)
    comment_text = models.TextField(verbose_name='Текст комментария')
    comment_date = models.DateTimeField(verbose_name='Дата добавления комментария', auto_now_add=True)
    reply = models.ForeignKey('self', on_delete=models.CASCADE, verbose_name='Ответ комментарию', null=True, blank=True)
    is_active = models.BooleanField(verbose_name='Выводить на экран?', default=True)
    is_edited = models.BooleanField(verbose_name='Изменен?', default=False)

    def __str__(self):
        return self.comment_text

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('article', '-comment_date')


class CommentUser(models.Model):
    """Модель комментария для пользователя"""

    author = models.ForeignKey(AdvUser, on_delete=models.CASCADE, verbose_name='Автор', null=True)
    comment_text = models.TextField(verbose_name='Текст комментария')
    comment_date = models.DateTimeField(verbose_name='Дата добавления комментария', auto_now_add=True)
    reply = models.ForeignKey('self', on_delete=models.CASCADE, verbose_name='Ответ комментарию', null=True, blank=True)
    is_active = models.BooleanField(verbose_name='Выводить на экран?', default=True)
    is_edited = models.BooleanField(verbose_name='Изменен?', default=False)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name='Пользователь', default=6)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.comment_text

    class Meta:
        verbose_name = 'Комментарий для пользователя'
        verbose_name_plural = 'Комментарии для пользователей'
        ordering = ('-comment_date',)
