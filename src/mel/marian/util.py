def filename_safety(filename):
  return ''.join([s for s in filename if s in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz -.01234456789'])
