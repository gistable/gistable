@app.route('/socket.io/websocket')
def socketio():
    s = request.environ['socketio']
    if s.on_connect():
        #print 'CONNECTED', locals()
        #s.send({'buffer': buffer})
        #s.broadcast({'announcement': s.session.session_id + ' connected'})
        pass
    game_id=None;game=None;cook=None;i_am='spectator';rdsub = redis.Redis('localhost')
    while True:
        messages = s.recv()

        print 'listening..'
        lres = rdsub.listen()
        for lrs in lres:
            lgameid = lrs['channel'].split(':')[1]
            if lrs['type']=='subscribe':
                break
            print 'DECODING %s'%lrs
            ldt = json.loads(lrs['data'])
            if ldt['op']=='chat':
                print 'SENDING BCASTED CHAT'
                s.send(json.dumps({'op':'chat','user':ldt['user'],'text':ldt['text']}))
            else:
                raise Exception( "wtf %s"%ldt)
            print 'HEARD %s'%lrs
            break
        print 'done listening'
        
        for msg in messages:
            dt = json.loads(msg)
            print 'GOT MSG %s'%dt
            if dt['op']=='connect':
                game_id = dt['gameid']
                cook = getauthcookie(dt['rawcookie'])
                game = get_game(game_id)
                if cook == game['p1cookie']: i_am='player1'
                elif cook == game.p2cookie:  i_am='player2'
                pubkey = 'publish:'+game_id
                print 'subscribing to game %s'%pubkey
                rdsub.subscribe(pubkey)
                print 'received connect on game %s, with auth cook %s. i am %s'%(game_id,cook,i_am)

            elif dt['op']=='send_chat':
                pubkey = 'publish:'+game_id
                pmsg = json.dumps({'op':'chat','user':i_am,'text':html(dt['text'])})
                print 'sending pub on %s : %s'%(pubkey,pmsg)
                rcpts = g.redis.publish(pubkey,pmsg)
                print '%s recipients'%rcpts
            else:
                raise Exception(dt)