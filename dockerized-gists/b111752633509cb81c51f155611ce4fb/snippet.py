def train_fn(model, optimizer, criterion, batch):
    x, y, lengths = batch

    x = Variable(x.cuda())
    y = Variable(y.cuda(), requires_grad=False)

    mask = Variable(torch.ByteTensor(x.size()).fill_(1).cuda(),
            requires_grad=False)
    for k, l in enumerate(lengths):
        mask[:l, k, :] = 0

    hidden = model.init_hidden(x.size(1))
    y_hat = model.forward(x, hidden)

    # Apply mask
    y_hat.masked_fill_(mask, 0.0)
    y.masked_fill_(mask, 0.0)

    loss = criterion(y_hat, y)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    return loss.data[0]
